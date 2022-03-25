# Import flask dependencies
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db

# Import module models
from app.module_airservice.models import date_hour, air_quality_station, air_quality_data

# Define the blueprint: 'air', set its url prefix: app.url/air
module_airservice = Blueprint('air', __name__, url_prefix='/air')

# Set the route and accepted methods
@module_airservice.route('/station/<id>', methods=['GET'])
def air_station_readings(id):
    #result = AirQualityData.query.filter_by(EOIcodeStation=id).all()
    dh = date_hour(db.func.current_timestamp())
    db.session.add(dh)
    db.session.commit()
    return "Success", 200