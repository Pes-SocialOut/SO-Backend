# Import flask dependencies
# Import module models (i.e. User)
from app.module_event.models import Event
from datetime import date, datetime
from sqlalchemy.dialects.postgresql import UUID
from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for, jsonify)
import uuid

# Import the database object from the main app module
from app import db

# Define the blueprint: 'event', set its url prefix: app.url/event
module_event = Blueprint('event', __name__, url_prefix='/events')

# Set the route and accepted methods

# POST method: creates an event in the database
@module_event.route('', methods=['POST'])
def create_event():
    args = request.args

    # restriction 1: check for vulgar words in description and name

    # restriction 2: String attributes aren't empty    
    if len(args.get("id")) == 0 | len(args.get("name")) == 0 | len(args.get("description")) == 0 | len(args.get("userCreator")) == 0:
        return "An attribute is empty!", 400
    
    # restriction 3: date started is older than end date of the event
    dateStarted = datetime.strptime(args.get("dateStarted"), '%Y-%m-%d %H:%M:%S.%f')
    dateEnd= datetime.strptime(args.get("dateEnd"), '%Y-%m-%d %H:%M:%S.%f')
    #'2015-06-05 10:20:10.000'
    
    if dateStarted > dateEnd:
        return "date Started is bigger than date End, that's not possible!", 400
    
    # restriction 4: longitud and latitude in Catalunya

    # restriction 5: date started should be right now or in the future

    #STUCK HERE WITH THE DATES! I NEED TO GET THE DATESTARTED AND DATEEND AND DO COMPARISONS WITH THEM IN DATETIME FORMAT
    now = datetime.today
    if dateStarted < now:
        return "date Started earlier than right now, it already started?", 400

    # restriction 6: description attribute is longer than 250 characters
    if len(args.get("description")) > 250:
        return "Description is too long!", 400
    
    # restriction 7: name attribute is longer than 25 characters
    if len(args.get("name")) > 25:
        return "Name is too long!", 400
    
    
    event = Event(uuid.UUID(args.get("id")), args.get("name"), args.get("description"), args.get("dateCreated"), args.get("dateEnd"), uuid.UUID(args.get("userCreator")), args.get("longitud"), args.get("latitude"))
    db.session.add(event)
    db.session.commit()
    
    return jsonify({'event': event}), 201

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