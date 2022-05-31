# Import flask dependencies
# Import module models (i.e. User)
import sqlalchemy
from app.module_event.models import Event, Participant, Like, Review
from app.module_users.models import User, GoogleAuth
from app.module_admin.models import Admin
from app.module_airservice.controllers import general_quality_at_a_point
from app.module_users.utils import increment_achievement_of_user

from profanityfilter import ProfanityFilter
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from flask import (Blueprint, request, jsonify, current_app)
import uuid
import validators
import json

from app.module_calendar.functions_calendar import crearEvento, eliminarEventoTitle, editarEventoTitle, editarEventoDesciption

# Import the database object from the main app module
from app import db

# Define the blueprint: 'event', set its url prefix: app.url/event
module_event_v4 = Blueprint('event_v4', __name__, url_prefix='/v4/events')

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
@module_event_v4.route('/', methods=['POST'])
@jwt_required(optional=True)  # cambio esto y lo pongo en True
def create_event():
    try:
        args = request.json
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

    # Añadir evento al calendario del creador
    auth_id = uuid.UUID(get_jwt_identity())
    user = GoogleAuth.query.filter_by(id=auth_id).first()
    #token_victor = "ya29.a0ARrdaM8yuBz8zlr4SaWpxV39Z-80jwROwOaisqSAWQjOQddSx7dlK2diksCazQANU8JlZHBlHi99MWc3Gr6HexgepljLikE4s-5mtvd2yMNc_PVQqPu91Defpz_QCJKmFmMhNLymP5MsSotDYTVlp9qK0bVX"
    if user is not None:
        date_started_formatted = event.date_started.strftime("%Y-%m-%dT%H:%M:%S")
        date_end_formatted = event.date_end.strftime("%Y-%m-%dT%H:%M:%S")
        crearEvento(user.access_token, event.name, event.description, event.latitude, event.longitud, date_started_formatted, date_end_formatted)
    
    # Ejemplo de combinacion que funciona
    #auth_id = "ya29.a0ARrdaM8yuBz8zlr4SaWpxV39Z-80jwROwOaisqSAWQjOQddSx7dlK2diksCazQANU8JlZHBlHi99MWc3Gr6HexgepljLikE4s-5mtvd2yMNc_PVQqPu91Defpz_QCJKmFmMhNLymP5MsSotDYTVlp9qK0bVX"
    #crearEvento(user, "random guillem", "esto es un evento de prueba", 41.3713, 2.1494, '2022-05-10T09:00:00','2022-05-10T10:00:00')

    eventJSON = event.toJSON()
    return jsonify(eventJSON), 201


# MODIFICAR EVENTO: Modifica la información de un evento
# Recibe:
# PUT HTTP request con la id del evento en la URI y los atributos del evento en el body (formato JSON)
#       {name, description, date_started, date_end, user_creator, longitud, latitude, max_participants}
# Devuelve:
# - 400: Un objeto JSON con un mensaje de error
# - 200: Un objeto JSON con un mensaje de evento modificado con exito
@module_event_v4.route('/<id>', methods=['PUT'])
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

    # Canviar el calendario si el modify es correcto
    auth_id = uuid.UUID(get_jwt_identity())
    user = GoogleAuth.query.filter_by(id=auth_id).first()
    #token_victor = "ya29.a0ARrdaM8yuBz8zlr4SaWpxV39Z-80jwROwOaisqSAWQjOQddSx7dlK2diksCazQANU8JlZHBlHi99MWc3Gr6HexgepljLikE4s-5mtvd2yMNc_PVQqPu91Defpz_QCJKmFmMhNLymP5MsSotDYTVlp9qK0bVX"
    if user is not None:
        editarEventoDesciption(user.access_token, str(event.name), str(args.get("description")))
        editarEventoTitle(user.access_token, str(event.name), str(args.get("name")))
    
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
@module_event_v4.route('/<id>/join', methods=['POST'])
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

    # Añadir evento al calendario del usuario
    auth_id = uuid.UUID(get_jwt_identity())
    user = GoogleAuth.query.filter_by(id=auth_id).first()
    #token_victor = "ya29.a0ARrdaM8yuBz8zlr4SaWpxV39Z-80jwROwOaisqSAWQjOQddSx7dlK2diksCazQANU8JlZHBlHi99MWc3Gr6HexgepljLikE4s-5mtvd2yMNc_PVQqPu91Defpz_QCJKmFmMhNLymP5MsSotDYTVlp9qK0bVX"
    if user is not None:
        date_started_formatted = event.date_started.strftime("%Y-%m-%dT%H:%M:%S")
        date_end_formatted = event.date_end.strftime("%Y-%m-%dT%H:%M:%S")
        crearEvento(user.access_token, event.name, event.description, event.latitude, event.longitud, date_started_formatted, date_end_formatted)    


    return jsonify({"message": f"el usuario {user_id} se han unido CON EXITO"}), 200


# ABANDONAR EVENTO: Usuario abandona a un evento
# Recibe:
# POST HTTP request con la id del evento en la URI y el usuario que se quieran añadir al evento en el body (formato JSON)
#       {user_id}
# Devuelve:
# - 400: Un objeto JSON con un mensaje de error
# - 200: Un objeto JSON con un mensaje de el usuario ha abandonado el evento CON EXITO
@module_event_v4.route('/<id>/leave', methods=['POST'])
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

    # Eliminar el evento del calendario
    auth_id = uuid.UUID(get_jwt_identity())
    user = GoogleAuth.query.filter_by(id=auth_id).first()
    #token_victor = "ya29.a0ARrdaM8yuBz8zlr4SaWpxV39Z-80jwROwOaisqSAWQjOQddSx7dlK2diksCazQANU8JlZHBlHi99MWc3Gr6HexgepljLikE4s-5mtvd2yMNc_PVQqPu91Defpz_QCJKmFmMhNLymP5MsSotDYTVlp9qK0bVX"
    if user is not None:
        eliminarEventoTitle(user.access_token, event.name)

    return jsonify({"message": f"el participante {user_id} ha abandonado CON EXITO"}), 200


# DELETE EVENTO method: deletes an event from the database
@module_event_v4.route('/<id>', methods=['DELETE'])
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

    # Eliminar el evento del calendario
    auth_id = uuid.UUID(get_jwt_identity())
    user = GoogleAuth.query.filter_by(id=auth_id).first()
    if user is not None:
        eliminarEventoTitle(user.access_token, event.name)

    try:
        event.delete()
        return jsonify({"error_message": "Successful DELETE"}), 202
    except:
        return jsonify({"error_message": "error while deleting the event"}), 400