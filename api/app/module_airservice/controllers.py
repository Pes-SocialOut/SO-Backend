# Import flask dependencies
from flask import Blueprint, jsonify, request, render_template, flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db

# Import module models
from app.module_airservice.models import date_hour, air_quality_station, air_quality_data,polutant

# Define the blueprint: 'air', set its url prefix: app.url/air
module_airservice = Blueprint('air', __name__, url_prefix='/air')

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