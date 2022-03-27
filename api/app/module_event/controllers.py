# Import flask dependencies
# Import module models (i.e. User)
from re import M
from app.module_event.models import Event
from datetime import date, datetime
from sqlalchemy.dialects.postgresql import UUID
from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for, jsonify)
import uuid
import json

# Import the database object from the main app module
from app import db

# Define the blueprint: 'event', set its url prefix: app.url/event
module_event = Blueprint('event', __name__, url_prefix='/events')

# Min y Max longitud and latitude of Catalunya from resource https://www.idescat.cat/pub/?id=aec&n=200&t=2019
min_longitud_catalunya = 0.15
min_latitude_catalunya = 40.51667
max_longitud_catalunya = 3.316667
max_latitude_catalunya = 42.85

# Set the route and accepted methods

# POST method: creates an event in the database
@module_event.route('', methods=['POST'])
def create_event():
    args = request.args
    event_uuid = uuid.uuid4()

    # TODO restriction 1: check for vulgar words in description and name

    # restriction 2: String attributes aren't empty    
    if len(args.get("name")) == 0 | len(args.get("description")) == 0 | len(args.get("user_creator")) == 0:
        return jsonify({"error_message": "An attribute is empty!"}), 400
    
    # restriction 3: date started is older than end date of the event
    date_started = datetime.strptime(args.get("date_started"), '%Y-%m-%d %H:%M:%S')
    date_end= datetime.strptime(args.get("date_end"), '%Y-%m-%d %H:%M:%S')
    #'2015-06-05 10:20:10.000'
    if date_started > date_end:
        return jsonify({"error_message": "date Started is bigger than date End, that's not possible!"}), 400
    
    # restriction 4: longitud and latitude in Catalunya
    longitud = float(args.get("longitud"))
    latitude = float(args.get("latitude"))
    if max_longitud_catalunya < longitud or longitud < min_longitud_catalunya or max_latitude_catalunya < latitude or latitude < min_latitude_catalunya:
        return jsonify({"error_message": "location given by longitud and latitude are outside of Catalunya"}), 400
    
    # restriction 5: date started should be right now or in the future    
    if date_started < datetime.now():
        return jsonify({"error_message": "date Started earlier than right now, it already started?"}), 400

    # restriction 6: description attribute is longer than 250 characters
    if len(args.get("description")) > 250:
        return jsonify({"error_message": "Description is too long!"}), 400
    
    # restriction 7: name attribute is longer than 25 characters
    if len(args.get("name")) > 25:
        return jsonify({"error_message": "Name is too long!"}), 400
    
    # TODO restriction 8: max participants is bigger than MAX_PARTICIPANTS_NORMAL_EVENT

    
    event = Event(event_uuid, args.get("name"), args.get("description"), date_started, date_end, uuid.UUID(args.get("user_creator")), longitud, latitude, args.get("max_participants", type=int))
    db.session.add(event)
    
    # TODO Encontrar errores de base de datos como null value, usuario no existe, etc.
    try:
        db.session.commit()
    except:
        return jsonify({"error_message": "DO THIS"})
    
    eventJSON = event.toJSON()

    return jsonify(eventJSON), 201



# GET method: returns the information of one event
@module_event.route('', methods=['GET'])
def get_event():
    return "Always successful GET", 200

# DELETE method: deletes an event from the database
@module_event.route('', methods=['DELETE'])
def delete_event():
    return "Always successful DELETE", 200

# GET ALL method: returns the information of all the events of the database
@module_event.route('/', methods=['GET'])
def get_all_events():
    return "Always successful GET ALL", 200

# PUT method: Modifies the information of a specific event of the database
@module_event.route('', methods=['PUT'])
def modify_events():
    return "Always successful PUT", 200

# If the event doesn't exist
@module_event.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The event could not be found.</p>", 404

# TESTING THE DATABASE
@module_event.route('/', methods=['GET', 'POST'])
def event():

    # TODO: evententicate user
    example = Event('123e4567-e89b-12d3-a456-426614174000', 'Cesc', 'Es el puto amo', datetime(2015, 6, 5, 10, 20, 10, 10), datetime(2015, 6, 5, 10, 20, 10, 11),'123e4567-e29b-12d3-a456-426614174000')
    db.session.add(example)
    db.session.commit()

    return "Always successful", 200