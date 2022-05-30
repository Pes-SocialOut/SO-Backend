import pickle
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

estaciones = {8015001: {'ALTITUD': 6,
  'AREA URBANA': 2,
  'CODI COMARCA': 13,
  'CODI INE': 8015,
  'CONTAMINANT': 4948,
  'LATITUD': 41.443584,
  'LONGITUD': 2.23889,
  'TIPUS ESTACIO': 2},
 8015021: {'ALTITUD': 7,
  'AREA URBANA': 2,
  'CODI COMARCA': 13,
  'CODI INE': 8015,
  'CONTAMINANT': 1211,
  'LATITUD': 41.443985,
  'LONGITUD': 2.2378986,
  'TIPUS ESTACIO': 0},
 8019003: {'ALTITUD': 75,
  'AREA URBANA': 2,
  'CODI COMARCA': 13,
  'CODI INE': 8019,
  'CONTAMINANT': 2335,
  'LATITUD': 41.401128,
  'LONGITUD': 2.146942,
  'TIPUS ESTACIO': 2},
 8019004: {'ALTITUD': 3,
  'AREA URBANA': 2,
  'CODI COMARCA': 13,
  'CODI INE': 8019,
  'CONTAMINANT': 349,
  'LATITUD': 40.64299,
  'LONGITUD': 0.2884,
  'TIPUS ESTACIO': 0},
 8019039: {'ALTITUD': 12,
  'AREA URBANA': 2,
  'CODI COMARCA': 13,
  'CODI INE': 8019,
  'CONTAMINANT': 3220,
  'LATITUD': 41.422213,
  'LONGITUD': 2.190555,
  'TIPUS ESTACIO': 2},
 8019042: {'ALTITUD': 35,
  'AREA URBANA': 2,
  'CODI COMARCA': 13,
  'CODI INE': 8019,
  'CONTAMINANT': 60,
  'LATITUD': 41.117399,
  'LONGITUD': 1.241703,
  'TIPUS ESTACIO': 0},
 8019043: {'ALTITUD': 26,
  'AREA URBANA': 2,
  'CODI COMARCA': 13,
  'CODI INE': 8019,
  'CONTAMINANT': 1212,
  'LATITUD': 41.385315,
  'LONGITUD': 2.1537998,
  'TIPUS ESTACIO': 2},
 8019044: {'ALTITUD': 57,
  'AREA URBANA': 2,
  'CODI COMARCA': 13,
  'CODI INE': 8019,
  'CONTAMINANT': 15,
  'LATITUD': 41.193603,
  'LONGITUD': 1.236701,
  'TIPUS ESTACIO': 2},
 8019050: {'ALTITUD': 7,
  'AREA URBANA': 2,
  'CODI COMARCA': 13,
  'CODI INE': 8019,
  'CONTAMINANT': 5278,
  'LATITUD': 41.386403,
  'LONGITUD': 2.187398,
  'TIPUS ESTACIO': 0},
 8019054: {'ALTITUD': 136,
  'AREA URBANA': 2,
  'CODI COMARCA': 13,
  'CODI INE': 8019,
  'CONTAMINANT': 3989,
  'LATITUD': 41.426109,
  'LONGITUD': 2.148002,
  'TIPUS ESTACIO': 0},
 8019056: {'ALTITUD': 81,
  'AREA URBANA': 2,
  'CODI COMARCA': 13,
  'CODI INE': 8019,
  'CONTAMINANT': 310,
  'LATITUD': 41.389726,
  'LONGITUD': 2.115836,
  'TIPUS ESTACIO': 0},
 8019057: {'ALTITUD': 81,
  'AREA URBANA': 2,
  'CODI COMARCA': 13,
  'CODI INE': 8019,
  'CONTAMINANT': 1212,
  'LATITUD': 41.38749,
  'LONGITUD': 2.1151996,
  'TIPUS ESTACIO': 0},
 8019058: {'ALTITUD': 415,
  'AREA URBANA': 1,
  'CODI COMARCA': 13,
  'CODI INE': 8019,
  'CONTAMINANT': 1212,
  'LATITUD': 41.41843,
  'LONGITUD': 2.1238973,
  'TIPUS ESTACIO': 0},
 8022006: {'ALTITUD': 661,
  'AREA URBANA': 1,
  'CODI COMARCA': 14,
  'CODI INE': 8022,
  'CONTAMINANT': 1212,
  'LATITUD': 42.0979,
  'LONGITUD': 1.8482014,
  'TIPUS ESTACIO': 0},
 8058003: {'ALTITUD': 213,
  'AREA URBANA': 0,
  'CODI COMARCA': 3,
  'CODI INE': 8058,
  'CONTAMINANT': 4370,
  'LATITUD': 41.244883,
  'LONGITUD': 1.6177,
  'TIPUS ESTACIO': 0},
 8073001: {'ALTITUD': 27,
  'AREA URBANA': 2,
  'CODI COMARCA': 11,
  'CODI INE': 8073,
  'CONTAMINANT': 5766,
  'LATITUD': 41.35638,
  'LONGITUD': 2.076113,
  'TIPUS ESTACIO': 2},
 8074001: {'ALTITUD': 17,
  'AREA URBANA': 3,
  'CODI COMARCA': 17,
  'CODI INE': 8074,
  'CONTAMINANT': 3493,
  'LATITUD': 41.208614,
  'LONGITUD': 1.673054,
  'TIPUS ESTACIO': 0},
 8074005: {'ALTITUD': 5,
  'AREA URBANA': 1,
  'CODI COMARCA': 17,
  'CODI INE': 8074,
  'CONTAMINANT': 683,
  'LATITUD': 41.202198,
  'LONGITUD': 1.6722002,
  'TIPUS ESTACIO': 0},
 8080001: {'ALTITUD': 1120,
  'AREA URBANA': 0,
  'CODI COMARCA': 14,
  'CODI INE': 8080,
  'CONTAMINANT': 2345,
  'LATITUD': 42.177772,
  'LONGITUD': 1.835,
  'TIPUS ESTACIO': 1},
 8089002: {'ALTITUD': 15,
  'AREA URBANA': 2,
  'CODI COMARCA': 11,
  'CODI INE': 8089,
  'CONTAMINANT': 1546,
  'LATITUD': 41.303897,
  'LONGITUD': 2.000276,
  'TIPUS ESTACIO': 0},
 8089003: {'ALTITUD': 34,
  'AREA URBANA': 3,
  'CODI COMARCA': 11,
  'CODI INE': 8089,
  'CONTAMINANT': 1404,
  'LATITUD': 41.303038,
  'LONGITUD': 1.991389,
  'TIPUS ESTACIO': 0},
 8089004: {'ALTITUD': 12,
  'AREA URBANA': 3,
  'CODI COMARCA': 11,
  'CODI INE': 8089,
  'CONTAMINANT': 1570,
  'LATITUD': 41.300574,
  'LONGITUD': 2.013889,
  'TIPUS ESTACIO': 2},
 8089005: {'ALTITUD': 25,
  'AREA URBANA': 1,
  'CODI COMARCA': 11,
  'CODI INE': 8089,
  'CONTAMINANT': 1212,
  'LATITUD': 41.303097,
  'LONGITUD': 1.9914981,
  'TIPUS ESTACIO': 0},
 8096010: {'ALTITUD': 145,
  'AREA URBANA': 2,
  'CODI COMARCA': 41,
  'CODI INE': 8096,
  'CONTAMINANT': 3503,
  'LATITUD': 41.6153,
  'LONGITUD': 2.290834,
  'TIPUS ESTACIO': 2},
 8096011: {'ALTITUD': 145,
  'AREA URBANA': 3,
  'CODI COMARCA': 41,
  'CODI INE': 8096,
  'CONTAMINANT': 4152,
  'LATITUD': 41.599429,
  'LONGITUD': 2.279169,
  'TIPUS ESTACIO': 1},
 8096014: {'ALTITUD': 133,
  'AREA URBANA': 2,
  'CODI COMARCA': 41,
  'CODI INE': 8096,
  'CONTAMINANT': 1211,
  'LATITUD': 41.598682,
  'LONGITUD': 2.2870984,
  'TIPUS ESTACIO': 2},
 8101001: {'ALTITUD': 29,
  'AREA URBANA': 2,
  'CODI COMARCA': 13,
  'CODI INE': 8101,
  'CONTAMINANT': 319,
  'LATITUD': 41.193603,
  'LONGITUD': 1.236701,
  'TIPUS ESTACIO': 0},
 8102005: {'ALTITUD': 311,
  'AREA URBANA': 1,
  'CODI COMARCA': 6,
  'CODI INE': 8102,
  'CONTAMINANT': 321,
  'LATITUD': 41.5784,
  'LONGITUD': 1.6230061,
  'TIPUS ESTACIO': 1}}

#machine learning
@module_airservice_v1.route('/ml/', methods=['GET'])
def machine_learning():
        # Parametros JSON
    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido"}), 400 

   
    try:
        codi_eoi1 = float(request.args.get('codi_eoi1'))
        contaminant1 = float(request.args.get('contaminante1'))
        codi_eoi2 = float(request.args.get('codi_eoi2'))
        contaminant2 = float(request.args.get('contaminante2'))
        codi_eoi3 = float(request.args.get('codi_eoi3'))
        contaminant3 = float(request.args.get('contaminante3'))
        dia = float(request.args.get('dia'))
        mes = float(request.args.get('mes'))
        año = float(request.args.get('año'))
        hora = float(request.args.get('hora'))
        latitud = float(request.args.get('latitud'))
        longitud = float(request.args.get('longitud'))
    except ValueError:
        return jsonify({"error_message":"holita"}), 400
    
    try:
        filename = 'app/module_airservice/finalized_model.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        pred1 = {"CODI EOI": codi_eoi1, 
        "CONTAMINANT": contaminant1, 
        "TIPUS ESTACIO": estaciones[codi_eoi1]["TIPUS ESTACIO"], 
        "AREA URBANA" : estaciones[codi_eoi1]["AREA URBANA"], 
        "CODI INE": estaciones[codi_eoi1]["CODI INE"], 
        "CODI COMARCA": estaciones[codi_eoi1]["CODI COMARCA"], 
        "ALTITUD": estaciones[codi_eoi1]["ALTITUD"], 
        "LATITUD": estaciones[codi_eoi1]["LATITUD"], 
        "LONGITUD": estaciones[codi_eoi1]["LONGITUD"], 
        "Dia": dia, 
        "Mes": mes, 
        "Año": año, 
        "Hora": hora }
        pred2 = {"CODI EOI": codi_eoi2, 
        "CONTAMINANT": contaminant2, 
        "TIPUS ESTACIO": estaciones[codi_eoi2]["TIPUS ESTACIO"], 
        "AREA URBANA" : estaciones[codi_eoi2]["AREA URBANA"], 
        "CODI INE": estaciones[codi_eoi2]["CODI INE"], 
        "CODI COMARCA": estaciones[codi_eoi2]["CODI COMARCA"], 
        "ALTITUD": estaciones[codi_eoi2]["ALTITUD"], 
        "LATITUD": estaciones[codi_eoi2]["LATITUD"], 
        "LONGITUD": estaciones[codi_eoi2]["LONGITUD"], 
        "Dia": dia, 
        "Mes": mes, 
        "Año": año, 
        "Hora": hora }
        pred3 = {"CODI EOI": codi_eoi3, 
        "CONTAMINANT": contaminant3, 
        "TIPUS ESTACIO": estaciones[codi_eoi3]["TIPUS ESTACIO"], 
        "AREA URBANA" : estaciones[codi_eoi3]["AREA URBANA"], 
        "CODI INE": estaciones[codi_eoi3]["CODI INE"], 
        "CODI COMARCA": estaciones[codi_eoi3]["CODI COMARCA"], 
        "ALTITUD": estaciones[codi_eoi3]["ALTITUD"], 
        "LATITUD": estaciones[codi_eoi3]["LATITUD"], 
        "LONGITUD": estaciones[codi_eoi3]["LONGITUD"], 
        "Dia": dia, 
        "Mes": mes, 
        "Año": año, 
        "Hora": hora }
        
    except:
        return jsonify({"error_message":"Machine Learning Model failed , try again later..."}), 404

    
    pred1Ser = pd.Series(data=pred1, index=["CODI EOI", "CONTAMINANT", "TIPUS ESTACIO", "AREA URBANA" , "CODI INE", "CODI COMARCA", "ALTITUD", "LATITUD", "LONGITUD", "Dia", "Mes", "Año", "Hora" ])
    prediction1 = float(loaded_model.predict([pred1Ser]))

    pred2Ser = pd.Series(data=pred2, index=["CODI EOI", "CONTAMINANT", "TIPUS ESTACIO", "AREA URBANA" , "CODI INE", "CODI COMARCA", "ALTITUD", "LATITUD", "LONGITUD", "Dia", "Mes", "Año", "Hora" ])
    prediction2 = float(loaded_model.predict([pred2Ser]))

    pred3Ser = pd.Series(data=pred3, index=["CODI EOI", "CONTAMINANT", "TIPUS ESTACIO", "AREA URBANA" , "CODI INE", "CODI COMARCA", "ALTITUD", "LATITUD", "LONGITUD", "Dia", "Mes", "Año", "Hora" ])
    prediction3 = float(loaded_model.predict([pred3Ser]))

    w0, w1, w2 = barycentric_interpolation(estaciones[codi_eoi1]["LONGITUD"], estaciones[codi_eoi1]["LATITUD"], estaciones[codi_eoi2]["LONGITUD"], estaciones[codi_eoi2]["LATITUD"], estaciones[codi_eoi3]["LONGITUD"], estaciones[codi_eoi3]["LATITUD"], longitud, latitud)
    general_quality = w0*prediction1 + w1*prediction2 + w2*prediction3


    response = jsonify({'pollution': general_quality, "accuracy": 0.8286334127981916})
    response.status_code = 200
    return response
    

    return {"error_message": "all good"}
