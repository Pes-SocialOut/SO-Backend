# Import flask dependencies
from flask import Blueprint, jsonify, request #, render_template, flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db

# Import module models
from app.module_airservice.models import air_quality_station, air_quality_data, pollutant, triangulation_cache


# Import time libraries
from datetime import timedelta

# Import pickle library to save python objects to file
import pickle as pkl

# Define the blueprint: 'air', set its url prefix: app.url/air
module_airservice_v1 = Blueprint('air', __name__, url_prefix='/v1/air')

@module_airservice_v1.route('/stations/<id>', methods=['GET'])
def air_station_readings(id):
    query_result = air_quality_station.query.filter_by(eoi_code = id).first()
    if query_result == None:
        return jsonify({"error_message":f"Station with eoi_code {id} is not registered"}), 404
    st = query_result.toJSON()
    st['pollutants'] = []
    query_result = db.session.query(air_quality_data, pollutant) \
        .join(pollutant) \
        .filter(air_quality_data.station_eoi_code == id) \
        .filter(air_quality_data.date_hour == get_date_time_query_string(st['last_calculated_at'])) \
        .all()
    for measure, poll in query_result:
        ms = measure.toJSON()
        del ms['date_hour']
        del ms['station_eoi_code']
        ms['units'] = poll.units
        st['pollutants'].append(ms)
    return jsonify(st), 200

def get_date_time_query_string(now):
    yd = now - timedelta(days = 1)
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
    return response, 200

def barycentric_interpolation(x1, y1, x2, y2, x3, y3, xp, yp):
    w0 = ((y2-y3)*(xp-x3)+(x3-x2)*(yp-y3))/((y2-y3)*(x1-x3)+(x3-x2)*(y1-y3))
    w1 = ((y3-y1)*(xp-x3)+(x1-x3)*(yp-y3))/((y2-y3)*(x1-x3)+(x3-x2)*(y1-y3))
    return w0, w1, 1-w0-w1

@module_airservice_v1.route('/location/', methods=['POST'])
def general_quality_at_multiple_points():
    if 'points' not in request.json:
        return jsonify({'error_message':'Must contain json with "points" list, each point {ref_id, long, lat}'}), 400
    point_data = request.json['points']

    try:
        tri_query_result = triangulation_cache.query.first()
        triangulation_data = pkl.loads(tri_query_result.tri_object_bytes)
        triangulation_upd_time = tri_query_result.date_hour
    except:
        return jsonify({"error_message":"Service depends on data not currently available, try again later..."}), 404
    trifinder = triangulation_data['tri'].get_trifinder()
    triangles = triangulation_data['tri'].triangles
    air_data = triangulation_data['air']

    response = []
    for point in point_data:
        if not ('ref_id' in point and 'long' in point and 'lat' in point):
            continue
        ref_id = point['ref_id']
        long = point['long']
        lat = point['lat']

        triangle_id = trifinder(long, lat)
        if triangle_id == -1:
            continue

        triangle = triangles[triangle_id]
        
        s0 = air_data[triangle[0]]
        s1 = air_data[triangle[1]]
        s2 = air_data[triangle[2]]
        w0, w1, w2 = barycentric_interpolation(s0[1], s0[2], s1[1], s1[2], s2[1], s2[2], long, lat)
        general_quality = w0*s0[3] + w1*s1[3] + w2*s2[3]

        response.append({'ref_id': ref_id, 'pollution': general_quality})
    return jsonify({'triangulation_last_calculated_at': triangulation_upd_time, 'points': response}), 200
