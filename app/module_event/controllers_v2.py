# Import flask dependencies
# Import module models (i.e. User)
from unicodedata import name
from psycopg2 import IntegrityError
import sqlalchemy
from app.module_event.models import Event, Participant, Like
from datetime import datetime
from flask import (Blueprint, request, jsonify)
#from google.cloud import vision
import uuid
import validators

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

# CREAR EVENTO: Crea un evento en la base de datos
# Recibe:
# POST HTTP request con los atributos del nuevo evento en el body (formato JSON)
#       {name, description, date_started, date_end, user_creator, longitud, latitude, max_participants}
# Devuelve:
# - 400: Un objeto JSON con un mensaje de error
# - 201: Un objeto JSON con todos los parametros del evento creado (con la id incluida) 
@module_event_v2.route('/', methods=['POST'])
def create_event():
    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido!"}), 400 

    event_uuid = uuid.uuid4() 

    response = check_atributes(args)
    if (response['error_message'] != "all good"):
        return jsonify(response), 400
    
    date_started = datetime.strptime(args.get("date_started"), '%Y-%m-%d %H:%M:%S')
    date_end= datetime.strptime(args.get("date_end"), '%Y-%m-%d %H:%M:%S')
    longitud = float(args.get("longitud"))
    latitude = float(args.get("latitude"))
    max_participants = int(args.get("max_participants"))
    user_creator = uuid.UUID(args.get("user_creator"))


    event = Event(event_uuid, args.get("name"), args.get("description"), date_started, date_end, user_creator, longitud, latitude, max_participants, args.get("event_image_uri"))
    
    # Errores al guardar en la base de datos: FK violated, etc
    try:
        event.save()
    except sqlalchemy.exc.IntegrityError:
        return jsonify({"error_message": "User FK violated, el usuario user_creator no esta definido en la BD"}), 400
    except: 
        return jsonify({"error_message": "Error de DB nuevo, cual es?"}), 400

    # Añadir el creador al evento como participante
    participant = Participant(event.id, user_creator)

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
@module_event_v2.route('/<id>', methods=['PUT'])
def modify_events_v2(id):
    try:
        event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "la id no es una UUID valida"}), 400

    # Parametros JSON
    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido"}), 400 

    try:
        event = Event.query.filter_by(id = event_id).first()
    except:
        return jsonify({"error_message": "El evento no existe"}), 400
    
    # Comprobar atributos de JSON para ver si estan bien
    response = check_atributes(args)
    if (response['error_message'] != "all good"):
        return jsonify(response), 400

    # restricion: solo el usuario creador puede editar su evento
    if event.user_creator != uuid.UUID(args.get("user_creator")):
        return jsonify({"error_message": "solo el usuario creador puede modificar su evento"}), 400

    event.name = args.get("name")
    event.description = args.get("description")
    event.date_started = datetime.strptime(args.get("date_started"), '%Y-%m-%d %H:%M:%S')
    event.date_end= datetime.strptime(args.get("date_end"), '%Y-%m-%d %H:%M:%S')
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
def check_atributes(args):
    # restriccion 0: Mirar si los atributos estan en la URL
    if args.get("name") is None:
        return {"error_message": "atributo name no esta en la URL o es null"}
    if args.get("description") is None:
        return {"error_message": "atributo descripcion no esta en la URL o es null"}
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
    
    # restriccion 3: date started es mas grande que end date del evento (format -> 2015-06-05 10:20:10) y Comprobar Value Error
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
    
    # TODO restriccion 8: max participants es mas grande que MAX_PARTICIPANTS_NORMAL_EVENT o es mas pequeño que 2 (creator included) y Comprobar Value Error
    try:
        max_participants = int(args.get("max_participants"))
    except ValueError:
        return {"error_message": "max participants no es un mumero"}
    if max_participants < 2:
        return {"error_message": "el numero maximo de participantes ha de ser mas grande que 2"}

    # restriccion 9: imagen del evento no es una URL valida
    if not validators.url(args.get("event_image_uri")):
            return {"error_message": "la imagen del evento no es una URL valida"} 
        
    # TODO restriccion 10: mirar si la imagen es una imagen vulgar
    # event_image_uri = args.get("event_image_uri")
    # is_it_safe = detect_safe_search_uri(event_image_uri)
    # for category in is_it_safe:
    #     if(is_it_safe[category] == 'UNKNOWN' | is_it_safe[category] == 'POSSIBLE' | is_it_safe[category] == 'LIKELY' | is_it_safe[category] == 'VERY_LIKELY'):
    #         return {"error_message": "la imagen del evento no puede ser explicita (hemos detectado que podria serlo)"} 

    return {"error_message": "all good"}


def detect_safe_search_uri(uri):
    """Detects unsafe features in the file located in Google Cloud Storage or
    on the Web."""
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    is_it_safe = {}

    response = client.safe_search_detection(image=image)
    safe = response.safe_search_annotation

    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')
                    
    is_it_safe["adult"] = likelihood_name[safe.adult]
    is_it_safe["medical"] = likelihood_name[safe.medical]
    is_it_safe["spoofed"] = likelihood_name[safe.spoof]
    is_it_safe["violence"] = likelihood_name[safe.violence]
    is_it_safe["racy"] = likelihood_name[safe.racy]

    if response.error.message:
        return {"error_message": "la imagen del evento no se ha compilado correctamente"} 

    return is_it_safe


# UNIRSE EVENTO: Usuario se une a un evento
# Recibe:
# POST HTTP request con la id del evento en la URI y el usuario que se quieran añadir al evento en el body (formato JSON)
#       {user_id}
# Devuelve:
# - 400: Un objeto JSON con un mensaje de error
# - 200: Un objeto JSON con un mensaje de el usuario se ha unido con exito
@module_event_v2.route('/<id>/join', methods=['POST'])
def join_event(id):
    try:
        event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "la id del evento no es una UUID valida"}), 400

    try:
        event = Event.query.filter_by(id = event_id).first()
    except:
        return jsonify({"error_message":f"El evento {event_id} no existe en la BD"}), 400
    
    # TODO Mirar si el user puede unirse al evento (tema banear)
    
    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido"}), 400 

    try:
        user_id = uuid.UUID(args.get("user_id"))
    except:
        return jsonify({"error_message":f"la user_id {user_id} no es una UUID valida"}), 400
                
    # restriccion: el usuario creador no se puede unir a su propio evento (ya se une automaticamente al crear el evento)
    if event.user_creator == user_id:
        return jsonify({"error_message":
                f"El usuario {user_id} es el creador del evento (ya esta dentro)"}), 400

    participant = Participant(event_id, user_id)
    
    # Errores al guardar en la base de datos: FK violated, etc
    try:
        participant.save()
    except sqlalchemy.exc.IntegrityError:
        return jsonify({"error_message":f"FK violated, el usuario {user_id} ya se ha unido al evento o no esta definido en la BD"}), 400
    except:
        return jsonify({"error_message": "Error de DB nuevo, cual es?"}), 400

    return jsonify({"message":f"el usuario {user_id} se han unido CON EXITO"}), 200


# ABANDONAR EVENTO: Usuario abandona a un evento
# Recibe:
# POST HTTP request con la id del evento en la URI y el usuario que se quieran añadir al evento en el body (formato JSON)
#       {user_id}
# Devuelve:
# - 400: Un objeto JSON con un mensaje de error
# - 200: Un objeto JSON con un mensaje de el usuario ha abandonado el evento CON EXITO
@module_event_v2.route('/<id>/leave', methods=['POST'])
def leave_event(id):
    try:
        event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "la id del evento no es una UUID valida"}), 400

    try:
        event = Event.query.filter_by(id = event_id).first()
    except:
        return jsonify({"error_message":f"El evento {event_id} no existe en la BD"}), 400
        
    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido"}), 400 

    try:
        user_id = uuid.UUID(args.get("user_id"))
    except:
        return jsonify({"error_message":f"la user_id {user_id} no es una UUID valida"}), 400

    # restriccion: el usuario no es participante del evento
    try:
        participant = Participant.query.filter_by(event_id = event_id, user_id = user_id).first()
    except:
        return jsonify({"error_message":f"El usuario {user_id} no es participante del evento {event_id}"}), 400
    
    if participant is None:
        return jsonify({"error_message":f"El usuario {user_id} no es participante del evento {event_id}"}), 400

    # restriccion: el usuario creador no puede abandonar su evento
    if event.user_creator == user_id:
        return jsonify({"error_message":
                f"El usuario {user_id} es el creador del evento (no puede abandonar)"}), 400
    
    # Errores al guardar en la base de datos: FK violated, etc
    try:
        participant.delete()
    except sqlalchemy.exc.IntegrityError:
        return jsonify({"error_message":f"FK violated, el usuario {user_id} no esta definido en la BD"}), 400
    except:
        return jsonify({"error_message": "Error de DB nuevo, cual es?"}), 400

    return jsonify({"message":f"el participante {user_id} ha abandonado CON EXITO"}), 200

    



# GET method: returns the information of one event
@module_event_v2.route('/<id>', methods=['GET'])
# RECIBE:
# - GET HTTP request con la id del evento del que se quieren TODOS obtener los parametros
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 201: Un objeto JSON con TODOS los parametros del evento con la id de la request
def get_event(id):
    try:
        event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "Event_id isn't a valid UUID"}), 400

    try:
        event = Event.query.filter_by(id = event_id)
        return event.toJSON()
    except:
        return jsonify({"error_message": "The event doesn't exist"}), 400

# GET/user_creator method: devuelve todos los eventos creados por un usuario
@module_event_v2.route('/cretor/<id>', methods=['GET'])
# RECIBE:
# - GET HTTP request con la id del usuario del que se quieren obtener los eventos creados.
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida
# - 201: Un objeto JSON con TODOS los parametros del evento con la id de la request
def get_creations(id):
    try:
        user_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "Event_id isn't a valid UUID"}), 400

    try:
        events_creats = Event.query.filter_by(user_creator = user_id)
        return jsonify([event.toJSON() for event in events_creats]), 201
    except:
        return jsonify({"error_message": "An error has ocurred"}), 400        


# DELETE method: deletes an event from the database
@module_event_v2.route('/<id>', methods=['DELETE'])
# RECIBE:
# - DELETE HTTP request con la id del evento que se quiere eliminar
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON confirmando que se ha eliminado correctamente
def delete_event(id):
    try:
        user_id = uuid.UUID(id)
    except :
        return jsonify({"error_message": "User_id isn't a valid UUID"}), 400

    try:
        eventb = Event.query.filter_by(id = user_id)
        eventb.delete()
        return jsonify({"message": "Successful DELETE"}), 202
    except :
        return jsonify({"error_message": "The event doesn't exist"}), 400


# GET ALL method: returns the information of all the events of the database
@module_event_v2.route('/', methods=['GET'])
# RECIBE:
# - GET HTTP request
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error
# - 201: Un objeto JSON con todos los eventos que hay en el sistema
def get_all_events():
    try:
        all_events = Event.get_all()
        return jsonify([event.toJSON() for event in all_events])
    except Exception as e:
        return jsonify({"error_message": e}), 400


# If the event doesn't exist
@module_event_v2.errorhandler(404)
def page_not_found():
    return "<h1>404</h1><p>The event could not be found.</p>", 404

@module_event_v2.teardown_request
def teardown_request(exception):
    if exception:
        db.session.rollback()
    db.session.remove()


#Dar like: un usuario le da like a un evento
#POST method: crea un Like en la base de
@module_event_v2.route('/id', methods=['POST'])
#RECIBE:
#- POST HTTP request con los parametros en un JSON object en el body de la request.
#      {name, description, date_started, date_end, user_creator, longitud, latitude, max_participants}
#DEVUELVE:
#- 400: Un objeto JSON con un mensaje de error
#- 201: Un objeto JSON con todos los parametros del evento creado (con la id incluida) 
def create_like():

    try:
        args = request.json
    except:
        return jsonify({"error_message": "Mira el JSON body de la request, hay un atributo mal definido"}), 400

    user_id = args.get("user_id")
    event_id = args.get("event_id")

    try:
        user_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "User_id isn't a valid UUID"}), 400

    try:
        event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "Event_id isn't a valid UUID"}), 400
      
    Nuevo_like = Like(user_id, event_id)
    
    # TODO Encontrar errores de base de datos como null value, usuario no existe, etc.
    try:
        Nuevo_like.save()
    except:
        return jsonify({"error_message": " "})
    
    LikeJSON = Nuevo_like.toJSON()
    return jsonify(LikeJSON), 201

# DELETE method: deletes a like from the database
@module_event_v2.route('/<id>', methods=['DELETE'])
# RECIBE:
# - DELETE HTTP request con la id del evento que se quiere eliminar
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON confirmando que se ha eliminado correctamente
def delete_like(id):

    args = request.json
    delete_user_id = args.get("user_id")
    delete_event_id = args.get("event_id")

    try:
        delete_user_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "User_id isn't a valid UUID"}), 400

    try:
        delete_event_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "Event_id isn't a valid UUID"}), 400

    try:
        Like_borrar = Like.query.filter_by(user_id = delete_user_id, event_id = delete_event_id).first()
        Like_borrar.delete()
        return jsonify({"message": "Successful DELETE"}), 200
    except :
        return jsonify({"error_message": "The event doesn't exist"}), 400

# GET method: todos los eventos a los que un usuario ha dado like
@module_event_v2.route('/likes/<id>', methods=['GET'])
# RECIBE:
# - GET HTTP request con la id del usuario que queremos solicitar
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON confirmando que se ha eliminado correctamente
def get_likes_by_user(id):

    args = request.json
    user_id = args.get("user_id")

    try:
        user_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "User_id isn't a valid UUID"}), 400

    try:
        ides_likes = Like.query.filter_by(user_id = user_id)
        for ides in ides_likes:
            events += Event.query.filter_by(id = ides).first()
        return jsonify([event.toJSON() for event in events])
    except:
        return jsonify({"error_message": "The event doesn't exist"}), 400        

# FILTRAR EVENTO: Retorna un conjunto de eventos en base a unas caracteristicas
# Recibe:
# GET HTTP request con los atributos que quiere filtrar (formato JSON)
#       {name, date_started, date_end}
# Devuelve:
@module_event_v2.route('/Filter', methods=['GET'])
def filter_by():
    try:
        args = request.json
    except:
        return jsonify({"error_message": "The JSON body from the request is poorly defined"}), 400 

    if args.get("name") is not None:
        if len(args.get("name")) == 0:
            return {"error_message": "EL nom es un string incorrecte"}    

    if args.get("date_started") is not None or args.get("date_end") is not None:
        try:
            date_start_interval = datetime.strptime(args.get("date_started"), '%Y-%m-%d %H:%M:%S')
            date_end_interval = datetime.strptime(args.get("date_end"), '%Y-%m-%d %H:%M:%S')
            if date_start_interval > date_end_interval:
                return {"error_message": "The start date must be greater than the end date"}
            if date_start_interval == date_end_interval:
                return {"error_message": "The start date and the end date are the same" }
            if date_start_interval < datetime.now():
                return {"error_message": "Date_started is before the now time"}
        except ValueError:
            return {"error_message": "date_started or date_ended aren't real dates or they don't exist!"}

    try:
        events_filter = None
        if args.get("name") is not None:
            events_filter = Event.filter_by(name = args.get["name"])

        if args.get("date_started") is not None and args.get("name") is not None:
            events_filter = events_filter.filter_by(Event.date_started >= date_start_interval, Event.date_started <= date_end_interval, Event.date_end <= date_end_interval, )
        elif args.get("date_started") is not None:
            events_filter = Event.filter_by(Event.date_started >= date_start_interval, Event.date_started <= date_end_interval, Event.date_end <= date_end_interval, )

        if events_filter is None:
                return jsonify({"error_message": "Any event match with the filter"}), 400
        else:
            return jsonify([event.toJSON() for event in events_filter])
    except Exception as e:
        return jsonify({"error_message": e}), 400