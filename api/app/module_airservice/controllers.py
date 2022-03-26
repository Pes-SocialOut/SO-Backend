# Import flask dependencies
from flask import Blueprint, jsonify, request #, render_template, flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db

# Import module models
from app.module_airservice.models import date_hour, air_quality_station, air_quality_data, pollutant

# Define the blueprint: 'air', set its url prefix: app.url/air
module_airservice = Blueprint('air', __name__, url_prefix='/air')

# Import pickle library to save python objects to file
import pickle as pkl
import os
triangulation_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'triangulation.pkl')

# Set the route and accepted methods
@module_airservice.route('/station/<id>', methods=['GET'])
def air_station_readings(id):
    #queryresult = pollutant.query.filter_by(composition=id).all()

 
    obj = {
        'composition': "NO2",
        'common_lowerbound': 5.0,
        'common_upperbound': 12.0,
        'units': "m^3x2"
    }
    response = jsonify(obj)
    response.status_code = 200
    return response

@module_airservice.route('/location/', methods=['GET'])
def general_quality_at_a_point():
    if not (request.args.get('long') and request.args.get('lat')):
        return jsonify({"message":"Must contain a point defined by query parameters <long> and <lat>"}), 400
    
    try:
        long = float(request.args.get('long'))
        lat = float(request.args.get('lat'))
    except ValueError:
        return jsonify({"message":"<long> and <lat> query parameters must be of type float"}), 400

    # TODO: Quizás leer el fichero cada vez es muy ineficiente, buscar alternativa.
    try:
        with open(triangulation_file_path, 'rb') as inp:
            triangulation_data = pkl.load(inp)
    except FileNotFoundError:
        return jsonify({"message":"Service depends on a file not currently available, try again later..."}), 404

    # Find triangle
    trifinder = triangulation_data['tri'].get_trifinder()
    triangle_id = trifinder(long, lat)

    if triangle_id == -1:
        return jsonify({"message":"Point must be inside Catalunya's area"}), 400
    
    triangle = triangulation_data['tri'].triangles[triangle_id]
    air_data = triangulation_data['air']
    # Select stations
    s0 = air_data[triangle[0]]
    s1 = air_data[triangle[1]]
    s2 = air_data[triangle[2]]
    w0, w1, w2 = baricentric_interpolation(s0[1], s0[2], s1[1], s1[2], s2[1], s2[2], long, lat)
    general_quality = w0*s0[3] + w1*s1[3] + w2*s2[3]

    js0 = {'id': s0[0], 'long': s0[1], 'lat': s0[2], 'quality': s0[3]}
    js1 = {'id': s1[0], 'long': s1[1], 'lat': s1[2], 'quality': s1[3]}
    js2 = {'id': s2[0], 'long': s2[1], 'lat': s2[2], 'quality': s2[3]}

    response = jsonify({'quality': general_quality, 'surrounding_quality_stations': [js0, js1, js2]})
    response.status_code = 200
    return response

def baricentric_interpolation(x1, y1, x2, y2, x3, y3, xp, yp):
    w0 = ((y2-y3)*(xp-x3)+(x3-x2)*(yp-y3))/((y2-y3)*(x1-x3)+(x3-x2)*(y1-y3))
    w1 = ((y3-y1)*(xp-x3)+(x1-x3)*(yp-y3))/((y2-y3)*(x1-x3)+(x3-x2)*(y1-y3))
    return w0, w1, 1-w0-w1