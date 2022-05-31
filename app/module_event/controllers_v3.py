# Import flask dependencies
# Import module models (i.e. User)
import sqlalchemy
from app.module_event.models import Event, Participant, Like, Review
from app.module_users.models import User, GoogleAuth
from app.module_admin.models import Admin
from app.module_airservice.controllers import general_quality_at_a_point
from app.module_users.utils import increment_achievement_of_user

from app.module_chat.controllers import crear_chat_back

from profanityfilter import ProfanityFilter
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from flask import (Blueprint, request, jsonify, current_app)
import uuid
import validators
import json

# Import the database object from the main app module
from app import db

# Define the blueprint: 'event', set its url prefix: app.url/event
module_event_v3 = Blueprint('event_v3', __name__, url_prefix='/v3/events')

# Min y Max longitud and latitude of Catalunya from resource https://www.idescat.cat/pub/?id=aec&n=200&t=2019
min_longitud_catalunya = 0.15
max_longitud_catalunya = 3.316667

min_latitude_catalunya = 40.51667
max_latitude_catalunya = 42.85

# Set the route and accepted methods

# CREAR EVENTO: Crea un evento en la base de datos
# Recibe:
# POST HTTP request con los atributos del nuevo evento en el body (formato JSON)
#       {name, description, date_started, date_end, user_creator, longitud, latitude, max_participants}
# Devuelve:
# - 400: Un objeto JSON con un mensaje de error
# - 201: Un objeto JSON con todos los parametros del evento creado (con la id incluida)
@module_event_v3.route('/', methods=['POST'])
@jwt_required(optional=True)  # cambio esto y lo pongo en True
def create_event():
    try:
        args = request.json
        #args.noauth_local_webserver = True
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido!"}), 400

    event_uuid = uuid.uuid4()

    response = check_atributes(args, "create")
    if (response['error_message'] != "all good"):
        return jsonify(response), 400

    date_started = datetime.strptime(
        args.get("date_started"), '%Y-%m-%d %H:%M:%S')
    date_end = datetime.strptime(args.get("date_end"), '%Y-%m-%d %H:%M:%S')
    longitud = float(args.get("longitud"))
    latitude = float(args.get("latitude"))
    max_participants = int(args.get("max_participants"))
    user_creator = uuid.UUID(args.get("user_creator"))

  # restricion: solo puedes crear eventos para tu usuario (mirando Bearer Token)
    auth_id = get_jwt_identity()
    if str(user_creator) != auth_id:
        return jsonify({"error_message": "Un usuario no puede crear un evento por otra persona"}), 403

    event = Event(event_uuid, args.get("name"), args.get("description"), date_started, date_end,
                  user_creator, longitud, latitude, max_participants, args.get("event_image_uri"))

    # Errores al guardar en la base de datos: FK violated, etc
    try:
        event.save()
    except sqlalchemy.exc.IntegrityError:
        return jsonify({"error_message": "User FK violated, el usuario user_creator no esta definido en la BD"}), 400
    except:
        return jsonify({"error_message": "Error de DB nuevo, cual es?"}), 400

    # Añadir el creador al evento como participante
    participant = Participant(event.id, user_creator)

    # Si es el primer evento que crea, darle el noob host
    increment_achievement_of_user("noob_host", user_creator)

    try:
        participant.save()
    except sqlalchemy.exc.IntegrityError:
        return jsonify({"error_message": "FK violated"}), 400
    except:
        return jsonify({"error_message": "Error de DB nuevo, cual es?"}), 400

    eventJSON = event.toJSON()
    return jsonify(eventJSON), 201


# MODIFICAR EVENTO: Modifica la información de un evento
# Recibe:
# PUT HTTP request con la id del evento en la URI y los atributos del evento en el body (formato JSON)
#       {name, description, date_started, date_end, user_creator, longitud, latitude, max_participants}
# Devuelve:
# - 400: Un objeto JSON con un mensaje de error
# - 200: Un objeto JSON con un mensaje de evento modificado con exito
@module_event_v3.route('/<id>', methods=['PUT'])
@jwt_required(optional=False)
def modify_events_v2(id):
    try:
        event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": f"la id no es una UUID valida"}), 400

    # Parametros JSON
    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido"}), 400

    try:
        event = Event.query.get(event_id)
    except:
        return jsonify({"error_message": f"El evento {event_id} ha dado un error al hacer query"}), 400

    # Si el evento no existe
    if event is None:
        return jsonify({"error_message": f"El evento {event_id} no existe"}), 400

    # Comprobar atributos de JSON para ver si estan bien
    response = check_atributes(args, "modify")
    if (response['error_message'] != "all good"):
        return jsonify(response), 400

    # restricion: solo el usuario creador puede editar su evento
    if event.user_creator != uuid.UUID(args.get("user_creator")):
        return jsonify({"error_message": "solo el usuario creador puede modificar su evento"}), 400

    # restricion: solo el usuario creador puede modificar su evento (mirando Bearer Token)
    auth_id = get_jwt_identity()
    if str(event.user_creator) != auth_id:
        return jsonify({"error_message": "A user cannot update the events of others"}), 403

    event.name = args.get("name")
    event.description = args.get("description")
    event.longitud = float(args.get("longitud"))
    event.latitude = float(args.get("latitude"))
    event.max_participants = int(args.get("max_participants"))
    event.event_image_uri = args.get("event_image_uri")

    # Errores al guardar en la base de datos: FK violated, etc
    try:
        event.save()
    except sqlalchemy.exc.IntegrityError:
        return jsonify({"error_message": "User FK violated, el usuario user_creator no esta definido en la BD"}), 400
    except:
        return jsonify({"error_message": "Error de DB nuevo, cual es?"}), 400

    return jsonify({"message": "evento modificado CON EXITO"}), 200


# Metodo para comprobar los atributos pasados de un evento a crear o modificat (POST o PUT)
# Devuelve: Diccionario con un mensaje de error o un mensaje de todo bien
def check_atributes(args, type):
    # restriccion 0: Mirar si los atributos estan en el body
    if args.get("name") is None:
        return {"error_message": "atributo name no esta en el body o es null"}
    if args.get("description") is None:
        return {"error_message": "atributo description no esta en el body o es null"}
    if type != "modify":
        if args.get("date_started") is None:
            return {"error_message": "atributo date_started no esta en la URL o es null"}
        if args.get("date_end") is None:
            return {"error_message": "atributo date_end no esta en la URL o es null"}
    if args.get("user_creator") is None:
        return {"error_message": "atributo user_creator no esta en la URL o es null"}
    if args.get("longitud") is None:
        return {"error_message": "atributo longitud no esta en la URL o es null"}
    if args.get("latitude") is None:
        return {"error_message": "atributo latitud no esta en la URL o es null"}
    if args.get("max_participants") is None:
        return {"error_message": "atributo max_participants no esta en la URL o es null"}
    if args.get("event_image_uri") is None:
        return {"error_message": "atributo event_image_uri no esta en la URL o es null"}

    # restriccion 1: mirar las palabras vulgares en el nombre y la descripcion
    pf = ProfanityFilter()
    if pf.is_profane(args.get("name")):
        return {"error_message": "The name attribute is vulgar"}
    if pf.is_profane(args.get("description")):
        return {"error_message": "The description attribute is vulgar"}

    # restriccion 2: Atributos string estan vacios
    try:
        user_creator = uuid.UUID(args.get("user_creator"))
    except ValueError:
        return {"error_message": f"user_creator id isn't a valid UUID"}
    if not isinstance(args.get("name"), str):
        return {"error_message": "name isn't a string!"}
    if not isinstance(args.get("description"), str):
        return {"error_message": "description isn't a string!"}
    if len(args.get("name")) == 0 | len(args.get("description")) == 0 | len(str(user_creator)) == 0:
        return {"error_message": "name, description or user_creator is empty!"}

    # restriccion 3: date started es mas grande que end date del evento (format -> 2015-06-05 10:20:10) y Comprobar Value Error
    if type != "modify":
        try:
            date_started = datetime.strptime(
                args.get("date_started"), '%Y-%m-%d %H:%M:%S')
            date_end = datetime.strptime(args.get("date_end"), '%Y-%m-%d %H:%M:%S')
            if date_started > date_end:
                return {"error_message": f"date Started {date_started} is bigger than date End {date_end}, that's not possible!"}
        except ValueError:
            return {"error_message": f"date_started or date_ended aren't real dates or they don't exist!"}

    # restriccion 4: longitud y latitude en Catalunya y checkear Value Error
    try:
        longitud = float(args.get("longitud"))
        latitude = float(args.get("latitude"))
        if max_longitud_catalunya < longitud or longitud < min_longitud_catalunya or max_latitude_catalunya < latitude or latitude < min_latitude_catalunya:
            return {"error_message": "location given by longitud and latitude are outside of Catalunya"}
    except ValueError:
        return {"error_message": "longitud or latitude aren't floats!"}

    # restriccion 5: date started deberia ser ahora mismo o en el futuro
    if type != "modify":
      if date_started < datetime.now():
        return {"error_message": f"date Started {date_started} es antes de ahora mismo, ha comenzado ya?"}

    # restriccion 6: atributo description es mas grande que 250 characters
    if len(args.get("description")) > 250:
        return {"error_message": "Description es demasiado largo"}

    # restriccion 7: atributo name es mas grande que 25 characters
    if len(args.get("name")) > 25:
        return {"error_message": "Name es demasiado largo"}

    # TODO restriccion 8: max participants es mas grande que MAX_PARTICIPANTS_NORMAL_EVENT o es mas pequeño que 2 (creator included) y Comprobar Value Error
    try:
        max_participants = int(args.get("max_participants"))
    except ValueError:
        return {"error_message": "max participants no es un mumero"}
    if max_participants < 2:
        return {"error_message": f"el numero maximo de participantes ({max_participants}) ha de ser mas grande que 2"}

    # restriccion 9: imagen del evento no es una URL valida (pero si no hay no pasa nada)
    if len(args.get("event_image_uri")) != 0:
        if not validators.url(args.get("event_image_uri")):
            return {"error_message": "la imagen del evento no es una URL valida"}

    return {"error_message": "all good"}


# UNIRSE EVENTO: Usuario se une a un evento
# Recibe:
# POST HTTP request con la id del evento en la URI y el usuario que se quieran añadir al evento en el body (formato JSON)
#       {user_id}
# Devuelve:
# - 400: Un objeto JSON con un mensaje de error
# - 200: Un objeto JSON con un mensaje de el usuario se ha unido con exito
@module_event_v3.route('/<id>/join', methods=['POST'])
@jwt_required(optional=False)
def join_event(id):
    try:
        event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "la id del evento no es una UUID valida"}), 400

    try:
        event = Event.query.get(event_id)
    except:
        return jsonify({"error_message": f"Error al hacer query de un evento"}), 400

    if event is None:
        return jsonify({"error_message": f"El evento {event_id} no existe en la BD"}), 400

    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido"}), 400

    try:
        user_id = uuid.UUID(args.get("user_id"))
    except:
        return jsonify({"error_message": f"la user_id no es una UUID valida"}), 400

    auth_id = get_jwt_identity()
    if str(user_id) != auth_id:
        return jsonify({"error_message": "A user cannot join a event for others"}), 403

    # restriccion: el usuario creador no se puede unir a su propio evento (ya se une automaticamente al crear el evento)
    if event.user_creator == user_id:
        return jsonify({"error_message": f"El usuario {user_id} es el creador del evento (ya esta dentro)"}), 400

    # restriccion: el usuario ya esta dentro del evento
    particip = Participant.query.filter_by(
        event_id=event_id, user_id=user_id).first()
    if particip is not None:
        return jsonify({"error_message": f"El usuario {user_id} ya esta dentro del evento {event_id}"}), 400

    # restriccion: el evento ya esta lleno
    num_participants = Participant.query.filter_by(event_id=event_id).all()
    if len(num_participants) >= event.max_participants:
        return jsonify({"error_message": f"El evento {event_id} ya esta lleno!"}), 400

    # restriccion: el evento ya esta pasado
    current_date = datetime.now() + timedelta(hours=2)
    if event.date_end <= current_date:
        return jsonify({"error_message": f"El evento {event_id} ya ha acabado!"}), 400

    participant = Participant(event_id, user_id)

    # Errores al guardar en la base de datos: FK violated, etc
    try:
        participant.save()
    except sqlalchemy.exc.IntegrityError:
        return jsonify({"error_message": f"FK violated, el usuario {user_id} ya se ha unido al evento o no esta definido en la BD"}), 400
    except:
        return jsonify({"error_message": "Error de DB nuevo, cual es?"}), 400

    # Si es un evento con contaminacion baja, se añade uno al achievement Social bug
    cont_level, cont_status = general_quality_at_a_point(event.longitud, event.latitude)
    if cont_status == 200:
        # Si es un evento con poca contaminacion, suma achievement Social Bug
        contaminacion = json.loads(cont_level.response[0])
        if contaminacion["pollution"] < 0.15:
            increment_achievement_of_user("social_bug",user_id)

    # Se crea un chat entre el participante y el creador
    crear_chat_back(event.id, user_id)

    return jsonify({"message": f"el usuario {user_id} se han unido CON EXITO"}), 200


# ABANDONAR EVENTO: Usuario abandona a un evento
# Recibe:
# POST HTTP request con la id del evento en la URI y el usuario que se quieran añadir al evento en el body (formato JSON)
#       {user_id}
# Devuelve:
# - 400: Un objeto JSON con un mensaje de error
# - 200: Un objeto JSON con un mensaje de el usuario ha abandonado el evento CON EXITO
@module_event_v3.route('/<id>/leave', methods=['POST'])
@jwt_required(optional=False)
def leave_event(id):
    try:
        event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "la id del evento no es una UUID valida"}), 400

    try:
        event = Event.query.get(event_id)
    except:
        return jsonify({"error_message": f"Error al hacer query de un evento"}), 400

    if event is None:
        return jsonify({"error_message": f"El evento {event_id} no existe en la BD"}), 400

    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido"}), 400

    try:
        user_id = uuid.UUID(args.get("user_id"))
    except:
        return jsonify({"error_message": f"la user_id no es una UUID valida"}), 400

    # restriccion: Un usuario no puede abandonar un evento por otro
    auth_id = get_jwt_identity()
    if str(user_id) != auth_id:
        return jsonify({"error_message": "A user cannot leave a event for others"}), 403

    # restriccion: el usuario no es participante del evento
    try:
        participant = Participant.query.filter_by(
            event_id=event_id, user_id=user_id).first()
    except:
        return jsonify({"error_message": f"Error en el query de participante"}), 400

    if participant is None:
        return jsonify({"error_message": f"El usuario {user_id} no es participante del evento {event_id}"}), 400

    # restriccion: el usuario creador no puede abandonar su evento
    if event.user_creator == user_id:
        return jsonify({"error_message":
                        f"El usuario {user_id} es el creador del evento (no puede abandonar)"}), 400

    # Errores al guardar en la base de datos: FK violated, etc
    try:
        participant.delete()
    except sqlalchemy.exc.IntegrityError:
        return jsonify({"error_message": f"FK violated, el usuario {user_id} no esta definido en la BD"}), 400
    except:
        return jsonify({"error_message": "Error de DB nuevo, cual es?"}), 400

    return jsonify({"message": f"el participante {user_id} ha abandonado CON EXITO"}), 200



# PARTICIPACIONES DE UN USER: todos los eventos a los que un usuario se ha unido
@module_event_v3.route('/joined/<id>', methods=['GET'])
# RECIBE:
# - GET HTTP request con la id del usuario que queremos solicitar
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON con los eventos a los que se a unido
@jwt_required(optional=False)
def get_user_joins(id):
    try:
        user_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": f"The user id isn't a valid UUID"}), 400

    try:
        events_joined = Participant.query.filter_by(user_id=user_id)
    except:
        return jsonify({"error_message": "Error when querying participants"}), 400
    try:
        events = []
        current_date = datetime.now() + timedelta(hours=2)
        for ides in events_joined:
            the_event = Event.query.get(ides.event_id)
            # Solo añadir los eventos ACTIVOS
            if the_event.date_end >= current_date:
                events.append(the_event)
        return jsonify([event.toJSON() for event in events]), 200
    except:
        return jsonify({"error_message": "Unexpected error"}), 400


# OBTENER UN EVENTO: returns the information of one event
@module_event_v3.route('/<id>', methods=['GET'])
# RECIBE:
# - GET HTTP request con la id del evento del que se quieren TODOS obtener los parametros
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 201: Un objeto JSON con TODOS los parametros del evento con la id de la request
@jwt_required(optional=False)
def get_event(id):
    try:
        event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": f"The event id isn't a valid UUID"}), 400

    try:
        event = Event.query.get(event_id)
    except:
        return jsonify({"error_message": f"The event {event_id} doesn't exist"}), 400

    # Si es un evento con contaminacion baja, se añade uno al achievement Healthy Curiosity
    cont_level, cont_status = general_quality_at_a_point(event.longitud, event.latitude)
    if cont_status == 200:
        # Si es un evento con poca contaminacion, suma achievement Social Bug
        contaminacion = json.loads(cont_level.response[0])
        if contaminacion["pollution"] < 0.15:
            auth_id = get_jwt_identity()
            try:
                increment_achievement_of_user("healthy_curiosity", auth_id)
            except:
                return jsonify({"error_message": f"Error adding an achievement"}), 400

    return jsonify(event.toJSON()), 200


# OBTENER EVENTOS POR USUARIO CREADOR method: devuelve todos los eventos creados por un usuario
@module_event_v3.route('/creator', methods=['GET'])
# RECIBE:
# - GET HTTP request con la id del usuario del que se quieren obtener los eventos creados como query parameter.
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida
# - 201: Un objeto JSON con TODOS los parametros del evento con la id de la request
@jwt_required(optional=False)
def get_creations():
    try:
        args = request.args
    except:
        return jsonify({"error_message": "Error loading args"}), 400

    try:
        if args.get("userid") is None:
            return jsonify({"error_message": "the id of the user isn't in the URL as a query parameter with name userid :("}), 400
        else:
            user_id = uuid.UUID(args.get("userid"))
    except:
        return jsonify({"error_message": "userid isn't a valid UUID"}), 400

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error_message": f"User {user_id} doesn't exist"}), 400

    try:
        events_creats = Event.query.filter_by(user_creator=user_id)
        current_date = datetime.now() + timedelta(hours=2)
        active_events = []
         # Solo añadir los eventos ACTIVOS
        for event in events_creats:
            if event.date_end >= current_date:
                active_events.append(event)
        
        return jsonify([event.toJSON() for event in active_events]), 200
    except:
        return jsonify({"error_message": "An unexpected error ocurred"}), 400


# DELETE EVENTO method: deletes an event from the database
@module_event_v3.route('/<id>', methods=['DELETE'])
# RECIBE:
# - DELETE HTTP request con la id del evento que se quiere eliminar
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON confirmando que se ha eliminado correctamente
@jwt_required(optional=False)
def delete_event(id):
    try:
        event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "Event_id isn't a valid UUID"}), 400

    try:
        event = Event.query.get(event_id)
    except:
        return jsonify({"error_message": f"Error getting the event"}), 400

    if event is None:
        return jsonify({"error_message": f"The event {event_id} doesn't exist"}), 400

    # restricion: solo el usuario creador puede eliminar su evento (o un admin) (mirando Bearer Token)
    auth_id = get_jwt_identity()
    if str(event.user_creator) != auth_id and not Admin.exists(auth_id):
        return jsonify({"error_message": "A user cannot delete events if they are not the creator"}), 403

    # Eliminar todos los participantes del evento ANTES DE ELIMINAR EL EVENTO
    try:
        participants = Participant.query.filter_by(event_id=event_id).all()
    except:
        return jsonify({"error_message": "error while querying participants of an event"}), 400

    for p in participants:
        try:
            p.delete()
        except:
            return jsonify({"error_message": "error while deleting participants of an event"}), 400

    # Eliminar todos los likes del evento ANTES DE ELIMINAR EL EVENTO
    try:
        likes = Like.query.filter_by(event_id=event_id).all()
    except:
        return jsonify({"error_message": "error while querying likes of an event"}), 400

    for l in likes:
        try:
            l.delete()
        except:
            return jsonify({"error_message": "error while deleting likes of an event"}), 400

   # Eliminar las reviews de un evento ANTES DE ELIMINAR EL EVENTO
    try:
        reviews = Review.query.filter_by(event_id=event_id).all()
    except:
        return jsonify({"error_message": "error while querying likes of an event"}), 400

    for r in reviews:
        try:
            r.delete()
        except:
            return jsonify({"error_message": "error while deleting reviews of an event"}), 400

    try:
        event.delete()
        return jsonify({"error_message": "Successful DELETE"}), 202
    except:
        return jsonify({"error_message": "error while deleting the event"}), 400


# GET ALL EVENTOS ACTIVOS method: retorna toda la informacion de todos los eventos activos de la database
@module_event_v3.route('/', methods=['GET'])
# RECIBE:
# - GET HTTP request
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error
# - 201: Un objeto JSON con todos los eventos activos que hay en el sistema
@jwt_required(optional=False)
def get_all_events():
    try:
        # La data de ahora es en GMT+2 por lo tanto tenemos que sumar dos horas en el tiempo actual
        current_date = datetime.now() + timedelta(hours=2)
        active_events = Event.query.filter(Event.date_end >= current_date)
    except:
        return jsonify({"error_message": "Error when querying events"}), 400

    try:
        return jsonify([event.toJSON() for event in active_events]), 200
    except:
        return jsonify({"error_message": "Unexpected error when passing events to JSON format"}), 400


# FILTRAR EVENTO: Retorna un conjunto de eventos en base a unas caracteristicas
# Recibe:
# GET HTTP request con los atributos que quiere filtrar (formato JSON)
#       {name, date_started, date_end}
# Devuelve:
@module_event_v3.route('/filter', methods=['GET'])
@jwt_required(optional=False)
def filter_by():
    try:
        args = request.json
    except:
        return jsonify({"error_message": "The JSON body from the request is poorly defined"}), 400

    if args.get("name") is not None:
        if len(args.get("name")) == 0:
            return {"error_message": "The name is not defined!"}

    if args.get("date_started") is not None or args.get("date_end") is not None:
        try:
            date_start_interval = datetime.strptime(
                args.get("date_started"), '%Y-%m-%d %H:%M:%S')
            date_end_interval = datetime.strptime(
                args.get("date_end"), '%Y-%m-%d %H:%M:%S')
            if date_start_interval > date_end_interval:
                return {"error_message": "The start date must be greater than the end date"}
            if date_start_interval == date_end_interval:
                return {"error_message": "The start date and the end date are the same"}
            if date_start_interval < datetime.now():
                return {"error_message": "Date_started is before the now time"}
        except ValueError:
            return {"error_message": "date_started or date_ended aren't real dates or they don't exist!"}

    try:
        events_filter = None
        if args.get("name") is not None:
            events_filter = Event.filter_by(name=args.get["name"])

        if args.get("date_started") is not None and args.get("name") is not None:
            events_filter = events_filter.filter_by(
                Event.date_started >= date_start_interval, Event.date_started <= date_end_interval, Event.date_end <= date_end_interval, )
        elif args.get("date_started") is not None:
            events_filter = Event.filter_by(Event.date_started >= date_start_interval,
                                            Event.date_started <= date_end_interval, Event.date_end <= date_end_interval, )

        if events_filter is None:
            return jsonify({"error_message": "Any event match with the filter"}), 400
        else:
            return jsonify([event.toJSON() for event in events_filter]), 200
    except Exception as e:
        return jsonify({"error_message": "hello"}), 400


# OBTENER LOS 10 EVENTOS CREAS MAS RECIENTEMENTE method: Retorna un conjunto con los 10 eventos mas recientes
@module_event_v3.route('/lastten', methods=['GET'])
@jwt_required(optional=False)
def lastest_events():
    try:
        # La data de ahora es en GMT+2 por lo tanto tenemos que sumar dos horas en el tiempo actual
        current_date = datetime.now() + timedelta(hours=2)
        lasts_events = Event.query.filter(Event.date_end >= current_date).order_by(Event.date_creation.desc()).all()
    except:
        return {"error_message": "Error while querying events"}

    lastten = []
    i = 0
    for e in lasts_events:
        if i < 10:
            lastten.append(e)
            i += 1
        else:
            break

    return jsonify([event.toJSON() for event in lastten]), 200


# SABER QUE PERSONAS SE HAN UNIDO A UN EVENTO method: Retorna el conjunto de users que se han unido a un evento
@module_event_v3.route('/participants', methods=['GET'])
@jwt_required(optional=False)
def who_joined_event():
    try:
        args = request.args
    except:
        return jsonify({"error_message": "Error loading args"}), 400

    try:
        if args.get("eventid") is None:
            return jsonify({"error_message": "the id of the event isn't in the URL as a query parameter with name eventid :("}), 400
        else:
            event_id = uuid.UUID(args.get("eventid"))
    except:
        return jsonify({"error_message": "eventid isn't a valid UUID"}), 400

    try:
        event = Event.query.get(event_id)
    except:
        return jsonify({"error_message": f"Error getting the event"}), 400

    if event is None:
        return jsonify({"error_message": f"The event {event_id} doesn't exist"}), 400

    # TODO todos pueden acceder a esta info?

    try:
        participants = Participant.query.filter_by(event_id=event_id)
    except:
        return jsonify({"error_message": "Error when querying participants"}), 400

    participant_list = []

    for p in participants:
        participant_list.append(p.user_id)

    return jsonify(participant_list), 200


# LISTAR TODOS LOS EVENTOS PASADOS DE UN USUARIO:
@module_event_v3.route('/pastevents', methods=['GET'])
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON con los atributos de la review creada
@jwt_required(optional=False)
def get_past_evento():
    try:
        args = request.args
    except:
        return jsonify({"error_message": "Error loading args"}), 400

    # restriccion: el user id tiene que estar en la URL y ser una UUID valida
    try:
        if args.get("userid") is None:
            return jsonify({"error_message": "the id of the user isn't in the URL as a query parameter with name userid :("}), 400
        else:
            user_id = uuid.UUID(args.get("userid"))
    except:
        return jsonify({"error_message": "eventid isn't a valid UUID"}), 400
    
    # restriccion: el user ha de existir
    try:
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"error_message": f"User {user_id} doesn't exist"}), 400
    except:
        return jsonify({"error_message": f"user {user} doesn't exist"}), 400

    # restricion: solo el usuario creador puede eliminar su evento (mirando Bearer Token)
    auth_id = get_jwt_identity()
    if str(user_id) != auth_id:
        return jsonify({"error_message": "A user cannot see the events that another user participated in"}), 403


    # if events_of_participant is None, it means that the user doesn't participate in any event
    events_of_participant = Participant.query.filter_by(user_id=user_id)

    # La data de ahora es en GMT+2 por lo tanto tenemos que sumar dos horas en el tiempo actual
    current_date = datetime.now() + timedelta(hours=2)
    past_events = []        

    for ev in events_of_participant:
        try:
            the_event = Event.query.get(ev.event_id)
            # eventos de un participantes NO INCLUYEN tus eventos
            if the_event.user_creator != user_id:
                if the_event.date_end <= current_date:
                    past_events.append(the_event)
        except:
            return jsonify({"error_message": "Error when querying events"}), 400

    try:
        return jsonify([event.toJSON() for event in past_events]), 200
    except:
        return jsonify({"error_message": "Unexpected error when passing events to JSON format"}), 400




########################################################################### O T R O S ########################################################


# If the event doesn't exist
@module_event_v3.errorhandler(404)
def page_not_found():
    return "<h1>404</h1><p>The event could not be found.</p>", 404


@module_event_v3.teardown_request
def teardown_request(exception):
    if exception:
        db.session.rollback()
    db.session.remove()


########################################################################### L I K E S #############################################################


# DAR LIKE method: un usuario le da like a un evento
@module_event_v3.route('/<id>/like', methods=['POST'])
# RECIBE:
# - POST HTTP request con los parametros en un JSON object en el body de la request.
# DEVUELVE:
# - 400: Un objeto JSON con un mensaje de error
@jwt_required(optional=False)
def create_like(id):
    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido"}), 400

    try:
        user_id = uuid.UUID(args.get("user_id"))
    except:
        return jsonify({"error_message": "User_id isn't a valid UUID"}), 400

    # Un usuario solo puede dar like por si mismo
    auth_id = get_jwt_identity()
    if str(user_id) != auth_id:
        return jsonify({"error_message": "A user can't like for others"}), 403

    try:
        event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "Event_id isn't a valid UUID"}), 400

    # Mirar si el evento existe
    find_event = Event.query.get(event_id)
    if find_event is None:
        return jsonify({"error_message": f"The event {event_id} doesn't exist"}), 400

    Nuevo_like = Like(user_id, event_id)

    try:
        Nuevo_like.save()
    except sqlalchemy.exc.IntegrityError:
        return jsonify({"error_message": "El usuario ya ha dado like a este evento"})
    except:
        return jsonify({"error_message": "Error nuevo de base de datos, ¿cual es?"})

    LikeJSON = Nuevo_like.toJSON()
    return jsonify(LikeJSON), 201


# QUITAR LIKE method: deletes a like from the database
@module_event_v3.route('/<id>/dislike', methods=['POST'])
# RECIBE:
# - DELETE HTTP request con la id del evento que se quiere eliminar
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON confirmando que se ha eliminado correctamente
@jwt_required(optional=False)
def delete_like(id):
    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido"}), 400

    try:
        delete_user_id = uuid.UUID(args.get("user_id"))
    except:
        return jsonify({"error_message": "User_id isn't a valid UUID"}), 400

    auth_id = get_jwt_identity()
    if str(delete_user_id) != auth_id:
        return jsonify({"error_message": "A user can't remove likes for others"}), 403

    try:
        delete_event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "Event_id isn't a valid UUID"}), 400

    event = Event.query.get(delete_event_id)
    if event is None:
        return jsonify({"error_message": f"The event {str(delete_event_id)} doesn't exist"}), 400

    try:
        Like_borrar = Like.query.filter_by(
            user_id=delete_user_id, event_id=delete_event_id).first()
        Like_borrar.delete()
        return jsonify({"message": "Successful DELETE"}), 200
    except:
        return jsonify({"error_message": f"The like of user {delete_user_id} in event {delete_event_id} doesn't exist"}), 400


# LIKES DE UN USER: todos los eventos a los que un usuario ha dado like
@module_event_v3.route('/like/<iduser>', methods=['GET'])
# RECIBE:
# - GET HTTP request con la id del usuario que queremos solicitar
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON confirmando que se ha eliminado correctamente
@jwt_required(optional=False)
def get_likes_by_user(iduser):
    try:
        user_id = uuid.UUID(iduser)
    except:
        return jsonify({"error_message": "User_id isn't a valid UUID"}), 400

    # No todos los usuarios pueden conseguir esta info (ESTO YA MIRA SI EL USUARIO EXISTE O NO, PQ LO COMPARA CON EL TOKEN QUE ES UN USUARIO QUE EXISTE SEGURO)
    auth_id = get_jwt_identity()
    if str(user_id) != auth_id:
        return jsonify({"error_message": "A user can't get the likes of the events of someone else"}), 403

    try:
        likes_user = Like.query.filter_by(user_id=user_id)
    except:
        return jsonify({"error_message": "Error when querying likes"}), 400
    try:
        events = []
        current_date = datetime.now() + timedelta(hours=2)
        for i in likes_user:
            the_event = Event.query.get(i.event_id)
            # Solo añadir los eventos ACTIVOS
            if the_event.date_end >= current_date:
                events.append(the_event)
        return jsonify([event.toJSON() for event in events]), 200
    except:
        return jsonify({"error_message": "Unexpected error"}), 400


# SABER SI USUARIO HA DADO LIKE A UN EVENTO method: saber si un usuario ha dado like a un evento
@module_event_v3.route('/<iduser>/like/<idevento>', methods=['GET'])
# RECIBE:
# - GET HTTP request con la id del usuario que queremos consultar
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON confirmando que se ha eliminado correctamente
@jwt_required(optional=False)
def get_likes_from_user(iduser, idevento):
    try:
        user_id_q = uuid.UUID(iduser)
    except:
        return jsonify({"error_message": "User_id isn't a valid UUID"}), 400

    user = User.query.get(user_id_q)
    if user is None:
        return jsonify({"error_message": f"User {user_id_q} doesn't exist"}), 400

    try:
        event_id_q = uuid.UUID(idevento)
    except:
        return jsonify({"error_message": "Event_id isn't a valid UUID"}), 400

    event = Event.query.get(event_id_q)
    if event is None:
        return jsonify({"error_message": f"Event {event_id_q} doesn't exist"}), 400

    try:
        liked = Like.query.filter_by(
            user_id=user_id_q, event_id=event_id_q).first()
    except:
        return jsonify({"error_message": "Error while querying Like"}), 400

    if liked is None:
        return jsonify({"message": "No le ha dado like"}), 200
    else:
        return jsonify({"message": "Le ha dado like"}), 200


# DIEZ EVENTOS CON MAYOR NUMERO DE LIKES: los 10 eventos con el mayor numero de likes
@module_event_v3.route('/topten', methods=['GET'])
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON con los top 10 eventos con mas likes
@jwt_required(optional=False)
def get_top_ten_events():
    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    engine = create_engine(db_uri)
    sql_query = db.text("select e.id, e.name, e.description, e.date_started, e.date_end, e.date_creation, e.user_creator, e.longitud, e.latitude, e.max_participants, e.event_image_uri from events e left join likes l on e.id = l.event_id where e.date_end >= CURRENT_TIMESTAMP group by e.id order by count(distinct l.user_id) desc limit 10;")
    with engine.connect() as conn:
        result_as_list = conn.execute(sql_query).fetchall() 

    top_ten_with_info = []
    for result in result_as_list:
        top_ten_with_info.append(dataToJSON(result))

    return jsonify([dataToJSON(event) for event in result_as_list]), 200


def dataToJSON(data):
    return {
        "id": data[0],
        "name": data[1],
        "description": data[2],
        "date_started": data[3],
        "date_end": data[4],
        "date_creation": data[5],
        "user_creator": data[6],
        "longitud": data[7],
        "latitude": data[8],
        "max_participants": data[9],
        "event_image_uri": data[10]
    }

########################################################################### R E V I E W S ##################################################################

# CREAR REVIEW: crear una review de un evento
@module_event_v3.route('/review', methods=['POST'])
# DEVUELVE:
# - 400 o 403: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON con los atributos de la review creada
@jwt_required(optional=False)
def crear_review():
    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido"}), 400

    # restriccion 0: Mirar si los atributos estan en el body
    if args.get("event_id") is None:
        return {"error_message": "atributo event_id no esta en el body o es null"}
    if args.get("user_id") is None:
        return {"error_message": "atributo user_id no esta en el body o es null"}
    if args.get("comment") is None:
        return {"error_message": "atributo comment no esta en el body, es null o esta vacio"}
    if args.get("rating") is None:
        return {"error_message": "atributo rating no esta en el body, es null"}

    # restriccion 1: event_id tiene que ser una UUID valida y tiene que existir
    try:
        event_id = uuid.UUID(args.get("event_id"))
    except:
        return jsonify({"error_message": "Event_id isn't a valid UUID"}), 400

    event = Event.query.get(event_id)
    if event is None:
        return jsonify({"error_message": f"Event {event_id} doesn't exist"}), 400

    # restriccion 2: El user_id tiene que ser una UUID valida
    try:
        user_id = uuid.UUID(args.get("user_id"))
    except:
        return jsonify({"error_message": "User_id isn't a valid UUID"}), 400

    # restriccion 3: Un usuario no puede dar una review por otra persona (por extra seguridad). Tmb implicitamente comprovamos si el usuario existe
    auth_id = get_jwt_identity()
    if str(user_id) != auth_id:
        return jsonify({"error_message": "A user can't create a review for others"}), 403

    # restriccion 4: el comentario tiene que ser una string y no puede ser mas largo que 500 caracteres
    if not isinstance(args.get("comment"), str):
        return {"error_message": "comment isn't a string!"}
    if len(args.get("comment")) == 0:
        return {"error_message": "comment can't be empty!"}
    if len(args.get("comment")) > 500:
        return {"error_message": "el comentario es demasiado largo, pasa los 500 caracteres"}

    # restriccion 5: Un rating ha de ser un integer entre 0 y 5
    try:
        rating = int(args.get("rating"))
    except ValueError:
        return jsonify({"error_message": "rating isn't an integer"}), 400
    if rating < 0 or rating > 5:
        return {"error_message": f"el rating de la review ({rating}) ha de ser mas grande que 0 y menos que 5"}

    # restriccion 6: el usuario ha de ser participante del evento (como eliminamos el participante despues de la review, no pueden estar duplicadas!)
    participant = Participant.query.filter_by(
        event_id=event_id, user_id=user_id).first()
    if participant is None:
        return jsonify({"error_message": f"El usuario {user_id} no es participante del evento {event_id}"}), 400

    # restriccion 7: el creador del evento no puede dar una review a su propio evento
    if user_id == event.user_creator:
        return jsonify({"error_message": "El creador del evento no puede dar una review a su propio evento"}), 400

    new_rating = Review(user_id=user_id, event_id=event_id,
                        rating=rating, comment=args.get("comment"))

    # Errores al guardar en la base de datos: FK violated, etc
    try:
        new_rating.save()
    except sqlalchemy.exc.IntegrityError:
        return jsonify({"error_message": "Integrity error, FK violated (algo no esta definido en la BD) o ya existe la review en la DB"}), 400
    except:
        return jsonify({"error_message": "Error de DB nuevo, cual es?"}), 400

    # Quitar el participante del evento
    try:
        participant.delete()
    except sqlalchemy.exc.IntegrityError:
        return jsonify({"error_message": "Integrity error, FK violated (algo no esta definido en la BD)"}), 400
    except:
        return jsonify({"error_message": "Error de DB nuevo, cual es?"}), 400

    # Si es la primera review de un usuario, darle el logro feedback monster
    increment_achievement_of_user("feedback_monster", user_id)

    # Devolver nueva review en formato JSON si todo ha funcionado correctamente
    ratingJSON = new_rating.toJSON()
    return jsonify(ratingJSON), 201


# LISTAR TODAS LAS REVIEW DE UN EVENTO: crear una review de un evento
@module_event_v3.route('/review', methods=['GET'])
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON con los atributos de la review creada
@jwt_required(optional=False)
def get_reviews_evento():  
    try:
        args = request.args
    except:
        return jsonify({"error_message": "Error loading args"}), 400

    # restriccion: el evento tiene que estar en la URL, ser una UUID valida y ha de existir
    try:
        if args.get("eventid") is None:
            return jsonify({"error_message": "the id of the event isn't in the URL as a query parameter with name eventid :("}), 400
        else:
            event_id = uuid.UUID(args.get("eventid"))
    except:
        return jsonify({"error_message": "eventid isn't a valid UUID"}), 400

    event = Event.query.get(event_id)
    if event is None:
        return jsonify({"error_message": f"Event {event_id} doesn't exist"}), 400
    
    user = User.query.filter_by(id = event.user_creator).first()
    
    try:
        reviews = Review.query.filter_by(event_id=event_id)
    except:
        return jsonify({"error_message": "Error querying the reviews"}), 400
    
    review_list = []

    for r in reviews:
        review_list.append(r)

    return jsonify({'event': event.toJSON(), 'username': user.username, 'email': user.email, 'reviews': [review.toJSON() for review in reviews]}), 200