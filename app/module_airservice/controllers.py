import pickle
import _pickle as cPickle
import bz2
import pandas as pd
from sklearn import metrics

# Import flask dependencies
from flask import Blueprint, jsonify, request #, render_template, flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db

# Import module models
from app.module_airservice.models import air_quality_station, air_quality_data, pollutant, triangulation_cache


# Import time libraries
from datetime import datetime, timedelta

# Import pickle library to save python objects to file
import pickle as pkl

# Define the blueprint: 'air', set its url prefix: app.url/air
module_airservice_v1 = Blueprint('air', __name__, url_prefix='/v1/air')

@module_airservice_v1.route('/stations/<id>', methods=['GET'])
def air_station_readings(id):
    qtime = get_date_time_query_string()
    query_result = db.session.query(air_quality_station, air_quality_data) \
        .outerjoin(air_quality_data, air_quality_station.eoi_code == air_quality_data.station_eoi_code) \
        .filter(air_quality_station.eoi_code == id) \
        .filter(air_quality_data.date_hour == qtime).all()

    if len(query_result) == 0:
        query_result = air_quality_station.query.filter_by(eoi_code = id).first()
        if query_result == None:
            return jsonify({"error_message":f"Station with eoi_code {id} is not registered"}), 404
        st = query_result.toJSON()
        st['pollutants'] = []
        return jsonify(st), 200
    
    response = query_result[0][0].toJSON()
    response['pollutants'] = []
    for _, measure in query_result:
        ms = measure.toJSON()
        del ms['date_hour']
        del ms['station_eoi_code']
        response['pollutants'].append(ms)
    
    return jsonify(response), 200

def get_date_time_query_string():
    yd = datetime.now() - timedelta(days = 1)
    if yd.minute > 30:
        yd += timedelta(hours = 1)
    return f'{yd.year}-{yd.month}-{yd.day} {yd.hour}:00:00'


@module_airservice_v1.route('/stations/', methods=['GET'])
def get_all_air_stations_id_name_location_pollution():
    query_result = air_quality_station.query.all()
    response = [{'id': s.eoi_code, 'name':s.name, 'long': s.longitude, 'lat': s.latitude, 'pollution': s.air_condition_scale} for s in query_result]
    return jsonify(response), 200


@module_airservice_v1.route('/location/', methods=['GET'])
def general_quality_at_a_point():
    if not (request.args.get('long') and request.args.get('lat')):
        return jsonify({"error_message":"Must contain a point defined by query parameters <long> and <lat>"}), 400
    
    try:
        long = float(request.args.get('long'))
        lat = float(request.args.get('lat'))
    except ValueError:
        return jsonify({"error_message":"<long> and <lat> query parameters must be of type float"}), 400

    try:
        tri_query_result = triangulation_cache.query.first()
        triangulation_data = pkl.loads(tri_query_result.tri_object_bytes)
        triangulation_upd_time = tri_query_result.date_hour
    except:
        return jsonify({"error_message":"Service depends on data not currently available, try again later..."}), 404

    # Encontrar triangulo
    trifinder = triangulation_data['tri'].get_trifinder()
    triangle_id = trifinder(long, lat)

    if triangle_id == -1:
        return jsonify({"error_message":"Point must be inside Catalunya's area"}), 400
    
    triangle = triangulation_data['tri'].triangles[triangle_id]
    air_data = triangulation_data['air']
    # Seleccionar estacion
    s0 = air_data[triangle[0]]
    s1 = air_data[triangle[1]]
    s2 = air_data[triangle[2]]
    w0, w1, w2 = barycentric_interpolation(s0[1], s0[2], s1[1], s1[2], s2[1], s2[2], long, lat)
    general_quality = w0*s0[3] + w1*s1[3] + w2*s2[3]

    json_stations = []
    if s0[0] != None:
        json_stations.append({'id': s0[0], 'long': s0[1], 'lat': s0[2], 'pollution': s0[3]})
    if s1[0] != None:
        json_stations.append({'id': s1[0], 'long': s1[1], 'lat': s1[2], 'pollution': s1[3]})
    if s2[0] != None:
        json_stations.append({'id': s2[0], 'long': s2[1], 'lat': s2[2], 'pollution': s2[3]})

    response = jsonify({'pollution': general_quality, 'triangulation_last_calculated_at': triangulation_upd_time, 'surrounding_measuring_stations': json_stations})
    response.status_code = 200
    return response

def barycentric_interpolation(x1, y1, x2, y2, x3, y3, xp, yp):
    w0 = ((y2-y3)*(xp-x3)+(x3-x2)*(yp-y3))/((y2-y3)*(x1-x3)+(x3-x2)*(y1-y3))
    w1 = ((y3-y1)*(xp-x3)+(x1-x3)*(yp-y3))/((y2-y3)*(x1-x3)+(x3-x2)*(y1-y3))
    return w0, w1, 1-w0-w1


#machine learning
@module_airservice_v1.route('/ml', methods=['GET'])
def machine_learning():
    tipus_estacio_mapping = {"peri-urban": 3.0, "background": 0.0, "industrial": 1.0, "traffic": 2.0}
    area_urbana_mapping = {"rural": 0.0, "suburban": 1.0, "urban": 2.0}
    
    try:
        codi_eoi1 = float(request.args.get('codi_eoi1'))
        contaminant1 = float(request.args.get('contaminante1'))
        codi_eoi2 = float(request.args.get('codi_eoi2'))
        contaminant2 = float(request.args.get('contaminante2'))
        codi_eoi3 = float(request.args.get('codi_eoi3'))
        contaminant3 = float(request.args.get('contaminante3'))
        dia = float(request.args.get('dia'))
        mes = float(request.args.get('mes'))
        year = float(request.args.get('year'))
        hora = float(request.args.get('hora'))
        latitud = float(request.args.get('latitud'))
        longitud = float(request.args.get('longitud'))
        filename = 'app/module_airservice/finalized_model.pbz2'
        loaded_model = cPickle.load(bz2.BZ2File(filename, 'rb'))
    except ValueError:
        return jsonify({"error_message":"Bad query params"}), 400

    try:
        query_result1 = air_quality_station.query.filter_by(eoi_code = request.args.get('codi_eoi1')).first()
        query_result2 = air_quality_station.query.filter_by(eoi_code = request.args.get('codi_eoi2')).first()
        query_result3 = air_quality_station.query.filter_by(eoi_code = request.args.get('codi_eoi3')).first()

        query_result1json = query_result1.toJSON()
        query_result2json = query_result2.toJSON()
        query_result3json = query_result3.toJSON()
        if query_result1 == None:
            return jsonify({"rror_message":f"Station with eoi_code {request.args.get('codi_eoi1')} is not registered"}), 404
            #return jsonify(query_result1.toJSON())
        if query_result2 == None:
            return jsonify({"rror_message":f"Station with eoi_code {request.args.get('codi_eoi2')} is not registered"}), 404
        if query_result3 == None:
            return jsonify({"rror_message":f"Station with eoi_code {request.args.get('codi_eoi3')} is not registered"}), 404
    

        
        
    except ValueError:
        return jsonify({"not stations"}), 400
    
    try:
        
        """pred1 = {"CODI EOI": codi_eoi1, 
        "CONTAMINANT": contaminant1, 
        "TIPUS ESTACIO": tipus_estacio_mapping[query_result1.station_type] , 
        "AREA URBANA" : area_urbana_mapping[query_result1.urban_area] , 
        "CODI INE": str(codi_eoi1)[0:4] , 
        "CODI COMARCA": query_result1.codi_comarca , 
        "ALTITUD": query_result1.altitude , 
        "LATITUD": query_result1.latitude , 
        "LONGITUD": query_result1.longitude , 
        "Dia": dia, 
        "Mes": mes, 
        "Año": year, 
        "Hora": hora }"""
        pred1 = {"CODI EOI": codi_eoi1, 
        "CONTAMINANT": contaminant1, 
        "TIPUS ESTACIO": tipus_estacio_mapping[query_result1json["station_type"]] , 
        "AREA URBANA" :area_urbana_mapping[query_result1json["urban_area"]], 
        "CODI INE": str(codi_eoi1)[0:4] , 
        "CODI COMARCA": query_result1.codi_comarca , 
        "ALTITUD": query_result1.altitude , 
        "LATITUD": query_result1.latitude , 
        "LONGITUD": query_result1.longitude , 
        "Dia": dia, 
        "Mes": mes, 
        "Año": year, 
        "Hora": hora }
    
    except ValueError:
        return jsonify({"error creating pred1"}), 400

    try:
        pred2 = {"CODI EOI": codi_eoi2, 
        "CONTAMINANT": contaminant2, 
        "TIPUS ESTACIO": tipus_estacio_mapping[query_result2json["station_type"]] , 
        "AREA URBANA" :area_urbana_mapping[query_result2json["urban_area"]], 
        "CODI INE": str(codi_eoi2)[0:4] , 
        "CODI COMARCA": query_result2.codi_comarca , 
        "ALTITUD": query_result2.altitude , 
        "LATITUD": query_result2.latitude , 
        "LONGITUD": query_result2.longitude , 
        "Dia": dia, 
        "Mes": mes, 
        "Año": year, 
        "Hora": hora }
        pred3 = {"CODI EOI": codi_eoi3, 
        "CONTAMINANT": contaminant3, 
        "TIPUS ESTACIO": tipus_estacio_mapping[query_result3json["station_type"]] , 
        "AREA URBANA" :area_urbana_mapping[query_result3json["urban_area"]], 
        "CODI INE": str(codi_eoi3)[0:4] , 
        "CODI COMARCA": query_result3.codi_comarca , 
        "ALTITUD": query_result3.altitude , 
        "LATITUD": query_result3.latitude , 
        "LONGITUD": query_result3.longitude , 
        "Dia": dia, 
        "Mes": mes, 
        "Año": year, 
        "Hora": hora }
        
        
        
    except:
        return jsonify({"error_message":"Machine Learning Model failed , try again later..."}), 404

    
    pred1Ser = pd.Series(data=pred1, index=["CODI EOI", "CONTAMINANT", "TIPUS ESTACIO", "AREA URBANA" , "CODI INE", "CODI COMARCA", "ALTITUD", "LATITUD", "LONGITUD", "Dia", "Mes", "Año", "Hora" ])
    prediction1 = float(loaded_model.predict([pred1Ser]))

    pred2Ser = pd.Series(data=pred2, index=["CODI EOI", "CONTAMINANT", "TIPUS ESTACIO", "AREA URBANA" , "CODI INE", "CODI COMARCA", "ALTITUD", "LATITUD", "LONGITUD", "Dia", "Mes", "Año", "Hora" ])
    prediction2 = float(loaded_model.predict([pred2Ser]))

    pred3Ser = pd.Series(data=pred3, index=["CODI EOI", "CONTAMINANT", "TIPUS ESTACIO", "AREA URBANA" , "CODI INE", "CODI COMARCA", "ALTITUD", "LATITUD", "LONGITUD", "Dia", "Mes", "Año", "Hora" ])
    prediction3 = float(loaded_model.predict([pred3Ser]))

    w0, w1, w2 = barycentric_interpolation(query_result1.longitude, query_result1.latitude, query_result2.longitude, query_result2.latitude, query_result3.longitude, query_result3.latitude, longitud, latitud)
    #w0, w1, w2 = barycentric_interpolation(estaciones[codi_eoi1]["LONGITUD"], estaciones[codi_eoi1]["LATITUD"], estaciones[codi_eoi2]["LONGITUD"], estaciones[codi_eoi2]["LATITUD"], estaciones[codi_eoi3]["LONGITUD"], estaciones[codi_eoi3]["LATITUD"], longitud, latitud)
    general_quality = w0*prediction1 + w1*prediction2 + w2*prediction3


    response = jsonify({'pollution': general_quality, "accuracy": 0.8286334127981916})
    response.status_code = 200
    return response
    

    return {"error_message": "all good"}
