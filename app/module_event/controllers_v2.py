# Import flask dependencies
# Import module models (i.e. User)
from app.module_event.models import Event
from datetime import datetime
from flask import (Blueprint, request, jsonify)
import uuid
# Import the database object from the main app module
from app import db

# Define the blueprint: 'event', set its url prefix: app.url/event
module_event_v2 = Blueprint('event_v2', __name__, url_prefix='/v2/events')

# Min y Max longitud and latitude of Catalunya from resource https://www.idescat.cat/pub/?id=aec&n=200&t=2019
min_longitud_catalunya = 0.15
max_longitud_catalunya = 3.316667

min_latitude_catalunya = 40.51667
max_latitude_catalunya = 42.85

# Set the route and accepted methods

# POST method: creates an event in the database
@module_event_v2.route('/', methods=['POST'])
# RECIBE:
# - POST HTTP request con los parametros en un JSON object en el body de la request.
#       {name, description, date_started, date_end, user_creator, longitud, latitude, max_participants}
# DEVUELVE:
# - 400: Un objeto JSON con un mensaje de error
# - 201: Un objeto JSON con todos los parametros del evento creado (con la id incluida) 
def create_event():
    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido!"}), 400 
    event_uuid = uuid.uuid4() 

    response = check_atributes(args)
    if (response.error_message != "all good"):
        return jsonify(response), 400
    
    date_started = datetime.strptime(args.get("date_started"), '%Y-%m-%d %H:%M:%S')
    date_end= datetime.strptime(args.get("date_end"), '%Y-%m-%d %H:%M:%S')
    longitud = float(args.get("longitud"))
    latitude = float(args.get("latitude"))
    max_participants = int(args.get("max_participants"))
    user_creator = uuid.UUID(args.get("user_creator"))
    
    event = Event(event_uuid, args.get("name"), args.get("description"), date_started, date_end, user_creator, longitud, latitude, max_participants)
    
    # TODO Encontrar errores de base de datos como null value, usuario no existe, etc.
    try:
        event.save()
    except:
        return jsonify({"error_message": " "})
    
    eventJSON = event.toJSON()
    return jsonify(eventJSON), 201

# Metodo PUT: Modifica la información de un evento
@module_event_v2.route('/<id>', methods=['PUT'])
# RECIBE:
# - PUT HTTP request con los parametros en un JSON object en el body de la request.
#       {name, description, date_started, date_end, user_creator, longitud, latitude, max_participants}
# DEVUELVE:
# - 400: Un objeto JSON con un mensaje de error
# - 201: Un objeto JSON con todos los parametros del evento modificado 
def modify_events_v2(id):
    try:
        event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "event_id no es una UUID valida"}), 400

    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido"}), 400 

    try:
        event = Event.query.filter_by(id = event_id)
    except:
        return jsonify({"error_message": "El evento no existe"}), 400
    
    #event.name = args.


# Metodo para comprobar los atributos pasados de un evento a crear o modificat (POST o PUT)
# returns: JSON with error_message or 
def check_atributes(args):
    # restriccion 0: Mirar si los atributos estan en la URL
    if args.get("name") is None:
        return {"error_message": "atributo name no esta en la URL"}
    if args.get("description") is None:
        return {"error_message": "atributo descripcion no esta en la URL"}
    if args.get("date_started") is None:
        return {"error_message": "atributo date_started no esta en la URL"}
    if args.get("date_end") is None:
        return {"error_message": "atributo date_end no esta en la URL"} 
    if args.get("user_creator") is None:
        return {"error_message": "atributo user_creator no esta en la URL"}
    if args.get("longitud") is None:
        return {"error_message": "atributo longitud no esta en la URL"} 
    if args.get("latitude") is None:
        return {"error_message": "atributo latitud no esta en la URL"} 
    if args.get("max_participants") is None:
        return {"error_message": "atributo max_participants no esta en la URL"} 

    # TODO restriccion 1: mirar las palabras vulgares en el nombre y la descripcion
    
    # restriccion 2: Atributos string estan vacios
    try:
        user_creator = uuid.UUID(args.get("user_creator"))
    except ValueError:
        return {"error_message": "user_creator isn't a valid UUID"}
    if not isinstance(args.get("name"), str):
        return {"error_message": "name isn't a string!"} 
    if not isinstance(args.get("description"), str):
        return {"error_message": "description isn't a string!"}
    if len(args.get("name")) == 0 | len(args.get("description")) == 0 | len(str(user_creator)) == 0:
        return {"error_message": "An attribute is empty!"}
    
    # restriccion 3: date started es mas grande que end date del evento (format -> 2015-06-05 10:20:10) AND Value Error check
    try:
        date_started = datetime.strptime(args.get("date_started"), '%Y-%m-%d %H:%M:%S')
        date_end= datetime.strptime(args.get("date_end"), '%Y-%m-%d %H:%M:%S')
        if date_started > date_end:
            return {"error_message": "date Started is bigger than date End, that's not possible!"}
    except ValueError:
        return {"error_message": "date_started or date_ended aren't real dates or they don't exist!"}
    
    # restriccion 4: longitud y latitude en Catalunya y checkear Value Error
    try:
        longitud = float(args.get("longitud"))
        latitude = float(args.get("latitude"))
        if max_longitud_catalunya < longitud or longitud < min_longitud_catalunya or max_latitude_catalunya < latitude or latitude < min_latitude_catalunya:
            return {"error_message": "location given by longitud and latitude are outside of Catalunya"}
    except ValueError:
        return {"error_message": "longitud or latitude aren't floats!"}

    # restriccion 5: date started deberia ser ahora mismo o en el futuro    
    if date_started < datetime.now():
        return {"error_message": "date Started antes de ahora mismo, ha comenzado ya?"}

    # restriccion 6: atributo description es mas grande que 250 characters
    if len(args.get("description")) > 250:
        return {"error_message": "Description es demasiado largo"}
    
    # restriccion 7: atributo name es mas grande que 25 characters
    if len(args.get("name")) > 25:
        return {"error_message": "Name es demasiado largo"}
    
    # TODO restriccion 8: max participants es mas grande que MAX_PARTICIPANTS_NORMAL_EVENT o es mas pequeño que 2 (creator included) y checkear Value Error
    try:
        max_participants = int(args.get("max_participants"))
    except ValueError:
        return {"error_message": "max participants no es un mumero"}
    
    return {"error_message": "all good"}


# GET method: returns the information of one event
@module_event_v2.route('/<id>', methods=['GET'])
def get_event(id):
    try:
        event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "event_id isn't a valid UUID"}), 400

    try:
        event = Event.query.filter_by(id = event_id)
        return event.toJSON()
    except:
        return jsonify({"error_message": "El evento no existe"}), 400

# DELETE method: deletes an event from the database
@module_event_v2.route('/<id>', methods=['DELETE'])
def delete_event(id):
    try:
        user_id = uuid.UUID(id)
    except :
        return jsonify({"error_message": "user_id isn't a valid UUID"}), 400

    try:
        eventb = Event.query.filter_by(id = user_id)
        eventb.delete()
        return jsonify({"message": "Successful DELETE"}), 200
    except :
        return jsonify({"error_message": "El evento no existe"}), 400

# GET ALL method: returns the information of all the events of the database
@module_event_v2.route('/', methods=['GET'])
def get_all_events():
    try:
        all_events = Event.get_all()
        return jsonify([event.toJSON() for event in all_events])
    except Exception as e:
        return jsonify({"error_message": e}), 400

# PUT v1 method: Modifies the information of a specific event of the database
@module_event_v2.route('/', methods=['PUT'])
def modify_events():
    return "Always successful PUT", 200


# If the event doesn't exist
@module_event_v2.errorhandler(404)
def page_not_found():
    return "<h1>404</h1><p>The event could not be found.</p>", 404
