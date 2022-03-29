# Import flask dependencies
# Import module models (i.e. User)
from app.module_event.models import Event
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for, jsonify)
import uuid
# Import the database object from the main app module
from app import db

# Define the blueprint: 'event', set its url prefix: app.url/event
module_event = Blueprint('event', __name__, url_prefix='/events')

# Min y Max longitud and latitude of Catalunya from resource https://www.idescat.cat/pub/?id=aec&n=200&t=2019
min_longitud_catalunya = 0.15
max_longitud_catalunya = 3.316667

min_latitude_catalunya = 40.51667
max_latitude_catalunya = 42.85

# Set the route and accepted methods

# POST method: creates an event in the database
@module_event.route('', methods=['POST'])
# RECEIVING:
# - POST HTTP request with the parameters {name, description, date_started, date_end, user_creator, longitud, latitude, max_participants}
#       in a JSON object in the body of the request
# RETURNS:
# - 400: A JSON object with the error message inside
# - 201: A JSON object with all the parameters of the created event (including the events id)
def create_event():
    try:
        args = request.json
    except:
        return jsonify({"error_message": "Check JSON body, there is an attribute not well defined!"}), 400 
    event_uuid = uuid.uuid4()

    # restriction 0: check if all attributes are in the URL
    if args.get("name") is None:
        return jsonify({"error_message": "name attribute is not in the URL!"}), 400 
    if args.get("description") is None:
        return jsonify({"error_message": "description attribute is not in the URL!"}), 400 
    if args.get("date_started") is None:
        return jsonify({"error_message": "date_started attribute is not in the URL!"}), 400 
    if args.get("date_end") is None:
        return jsonify({"error_message": "date_end attribute is not in the URL!"}), 400 
    if args.get("user_creator") is None:
        return jsonify({"error_message": "user_creator attribute is not in the URL!"}), 400 
    if args.get("longitud") is None:
        return jsonify({"error_message": "longitud attribute is not in the URL!"}), 400 
    if args.get("latitude") is None:
        return jsonify({"error_message": "latitude attribute is not in the URL!"}), 400 
    if args.get("max_participants") is None:
        return jsonify({"error_message": "max_participants attribute is not in the URL!"}), 400 

    # TODO restriction 1: check for vulgar words in description and name
    
    # restriction 2: String attributes aren't empty
    try:
        user_creator = uuid.UUID(args.get("user_creator"))
    except ValueError:
        return jsonify({"error_message": "user_creator isn't a valid UUID"}), 400
    if not isinstance(args.get("name"), str):
        return jsonify({"error_message": "name isn't a string!"}), 400 
    if not isinstance(args.get("description"), str):
        return jsonify({"error_message": "description isn't a string!"}), 400 
    if len(args.get("name")) == 0 | len(args.get("description")) == 0 | len(str(user_creator)) == 0:
        return jsonify({"error_message": "An attribute is empty!"}), 400
    
    # restriction 3: date started is older than end date of the event (format -> 2015-06-05 10:20:10) AND Value Error check
    try:
        date_started = datetime.strptime(args.get("date_started"), '%Y-%m-%d %H:%M:%S')
        date_end= datetime.strptime(args.get("date_end"), '%Y-%m-%d %H:%M:%S')
        if date_started > date_end:
            return jsonify({"error_message": "date Started is bigger than date End, that's not possible!"}), 400
    except ValueError:
        return jsonify({"error_message": "date_started or date_ended aren't real dates or they don't exist!"}), 400
    
    # restriction 4: longitud and latitude in Catalunya AND Value Error check
    try:
        longitud = float(args.get("longitud"))
        latitude = float(args.get("latitude"))
        if max_longitud_catalunya < longitud or longitud < min_longitud_catalunya or max_latitude_catalunya < latitude or latitude < min_latitude_catalunya:
            return jsonify({"error_message": "location given by longitud and latitude are outside of Catalunya"}), 400
    except ValueError:
        return jsonify({"error_message": "longitud or latitude aren't floats!"}), 400

    # restriction 5: date started should be right now or in the future    
    if date_started < datetime.now():
        return jsonify({"error_message": "date Started earlier than right now, it already started?"}), 400

    # restriction 6: description attribute is longer than 250 characters
    if len(args.get("description")) > 250:
        return jsonify({"error_message": "Description is too long!"}), 400
    
    # restriction 7: name attribute is longer than 25 characters
    if len(args.get("name")) > 25:
        return jsonify({"error_message": "Name is too long!"}), 400
    
    # TODO restriction 8: max participants is bigger than MAX_PARTICIPANTS_NORMAL_EVENT or is smaller than 2 (creator included) AND Value Error check
    try:
        max_participants = int(args.get("max_participants"))
    except ValueError:
        return jsonify({"error_message": "max participants isn't a number!"}), 400    

    event = Event(event_uuid, args.get("name"), args.get("description"), date_started, date_end, user_creator, longitud, latitude, max_participants)
    
    # TODO Encontrar errores de base de datos como null value, usuario no existe, etc.
    try:
        event.save()
    except:
        return jsonify({"error_message": " "})
    
    eventJSON = event.toJSON()
    return jsonify(eventJSON), 201



# GET method: returns the information of one event
@module_event.route('', methods=['GET'])
def get_event():

    args = request.json

    try:
        user_id = uuid.UUID(args.get("id"))
    except:
        return jsonify({"error_message": "user_id isn't a valid UUID"}), 400

    try:
        event = Event.query.filter_by(id = user_id)
        return event.toJSON()
    except:
        return jsonify({"error_message": "El evento no existe"}), 400

# DELETE method: deletes an event from the database
@module_event.route('', methods=['DELETE'])
def delete_event():

    args= request.json

    try:
        user_id = uuid.UUID(args.get("id"))
    except :
        return jsonify({"error_message": "user_id isn't a valid UUID"}), 400

    try:
        eventb = Event.query.filter_by(id = user_id)
        eventb.delete()
        return jsonify({"message": "Successful DELETE"}), 200
    except :
        return jsonify({"error_message": "El evento no existe"}), 400

# GET ALL method: returns the information of all the events of the database
@module_event.route('/', methods=['GET'])
def get_all_events():
    try:
        all_events = Event.get_all()
        return all_events.toJSON()
    except:
        return jsonify({"error_message": "Ha habido un error"}), 400

# PUT method: Modifies the information of a specific event of the database
@module_event.route('', methods=['PUT'])
def modify_events():
    return "Always successful PUT", 200

# If the event doesn't exist
@module_event.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The event could not be found.</p>", 404
