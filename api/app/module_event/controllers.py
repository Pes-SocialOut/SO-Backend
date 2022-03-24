# Import flask dependencies
# Import module models (i.e. User)
from app.module_event.models import Event
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
import uuid

# Import the database object from the main app module
from app import db

# Define the blueprint: 'event', set its url prefix: app.url/event
module_event = Blueprint('event', __name__, url_prefix='/events')

# Set the route and accepted methods

# TESTING THE DATABASE
@module_event.route('/', methods=['GET', 'POST'])
def event():

    # TODO: evententicate user
    example = Event('123e4567-e89b-12d3-a456-426614174000', 'Cesc', 'Es el puto amo', datetime(2015, 6, 5, 10, 20, 10, 10), datetime(2015, 6, 5, 10, 20, 10, 11),'123e4567-e29b-12d3-a456-426614174000')
    db.session.add(example)
    db.session.commit()

    return "Always successful", 200

# To get all the events
@module_event.route('/all', methods=['GET'])
def all_events():

    # TODO: return all events

    return "Always successful", 200

# If the event doesn't exist
@module_event.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404