# Import Flask dependences
# Import module models
import sqlalchemy
from app.module_chat.models import Message, Chat
from flask_jwt_extended import get_jwt_identity, jwt_required
import uuid
from flask import Blueprint, jsonify, request

# Define the blueprint: 'Message', set its url prefix: app.url/message
module_chat_v1 = Blueprint('chat', __name__, url_prefix= '/v1/chat')

# Crear Chat: create a new chat
# Recibe:
# POST HTTP request con los atributos del nuevo chat en el body(JSON)
#    {event_id, participant_id}
# Devuelve
# - 400: Un objeto JSON con un mensaje de error
# - 201: un objeto JSON con todos los parametros del nuevo chat(JSON)
@module_chat_v1.route('/', methods=['POST'])
def create_chat():
    try:
        args = request.json
    except: 
        return jsonify({"error message": "The JSON argument is bad defined"})

    if args.get("event_id") is None:
        return  jsonify({"error message": "Event if is not defined or its value is null"}), 400
    if args.get("creador_id") is None:
        return jsonify({ "error message": "Creador id is not defined or its value is null"}), 400
    if args.get("participant_id") is None:
        return jsonify({"error message": "Participant id is not defined or its value is null"}), 400
    
    try:
        event_id = uuid.UUID(args.get("event_id"))
    except:
        return jsonify({"error message": "The event id is not a valid uuid"}), 400

    try:
        creador_id = uuid.UUID(args.get("creador_id"))
    except:
        return jsonify({"error message": "The creator id is not a valid uuid"})

    try:
        participant_id = uuid.UUID(args.get("participant_id"))
    except:
        return jsonify({"error message": "The participant id is not a valid uuid"}), 400

    id = uuid.uuid4()

    New_Chat = Chat(id, event_id, creador_id, participant_id)

    try:
        New_Chat.save()
    except sqlalchemy.exc.IntegrityError:
       return jsonify({"error message": "FK problems, the user or the event doesn't exists"}), 400
    except:
        return jsonify({"error_message": "Something happened in the insert"}), 400
    
    return jsonify([New_Chat.toJSON()]), 201



# Crear Mensaje: create a new message
# Recibe:
# POST HTTP request con los atributos del nuevo mensaje en el body(JSON)
#       {userid, eventid, text}
# Devuelve
# - 400: Un objeto JSON con un mensaje de error
# - 201: Un objeto JSON con todos los parametros del nuevo mensaje(JSON)
@module_chat_v1.route('/Message', methods=['POST'])
def create_message():
    try: 
        args = request.json
    except:
        return jsonify({"error message": "The JSON argument is bad defined"}), 400

    if args.get("sender_id") is None:
        return jsonify({"error message": "Sender Id is not defined or its value is null"}), 400
    if args.get("chat_id") is None:
        return jsonify({"error message": "Chat Id is not defined or its value is null"}), 400
    if args.get("text") is None:
        return jsonify({"error message": "Text is not defined or its value is null"}), 400
    if not isinstance(args.get("text"), str):
        return jsonify({"error_message": "The text is not a string"}), 400

    try:
        sender_id = uuid.UUID(args.get("sender_id"))
    except:
        return jsonify({"error message": "The sender id not is a valid uuid"})
    
    try:
        chat_id = uuid.UUID(args.get("chat_id"))
    except:
        return jsonify({"error message": "The chat id not is a valid uuid"})

    id = uuid.uuid4()

    Message_new = Message(id, sender_id, chat_id, args.get("text"))

    try: 
        Message_new.save()
    #except sqlalchemy.exc.IntegrityError:
        #return jsonify({"error message": "FK problems, the user or the event doesn't exists"}), 400
    except:
        return jsonify({"error_message": "Something happened in the insert"}), 400

    return jsonify([Message_new.toJSON()]), 201

    

# DELETE method: deletes all the messages from an event
@module_chat_v1.route('/<id>', methods=['DELETE'])
# RECIBE:
# -DELETE HTTP request con la id del evento del cual se deben eliminar los mensajes
# DEVUELVE:
# -400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# -202: Un objeto JSON confirmando que se han borrado los debidos messages
def delete_event(id):

    try:
        event_id_esborrar = uuid.UUID(id)
    except: 
        return jsonify({"error message": "The event id isn't a valid UUID" }), 400

    try:
        A_borrar = Chat.query.filter_by(event_id = event_id_esborrar)
        for Chat_borrar in A_borrar:
            Messages = Message.query.filter_by(chat_id = Chat_borrar.id)
            for message in Messages:
                message.delete()
        for Chat_borrar in A_borrar:
            Chat_borrar.delete()
    except:
        return jsonify({"error message": "fallan borrar el chat"}), 400

    return jsonify({"message":f"The messages from this event have been succesfully deleted"}), 201

    
# GET method: get all chats from a user as creator
@module_chat_v1.route('/<id>', methods=['GET'])
# RECIBE:
    # GET HTTP request con la id del usuario del que queremos obtener los chats
# DEVUELVE
    # -202: Un objeto JSON con todos los Chats del usuario solicitado
    # -400: Un objeto JSON con los posibles mensajes de error, id no valida o usuario no existe
def get_user_creations(id):
    try: 
        user_id = uuid.UUID(id)
    except:
        return jsonify({"error message": "The user id isn't a valid uuid"}), 400

    try:
        chats_creador = Chat.query.filter_by(creador_id = user_id)
    except:
        return jsonify({"error message": "Chat no exist"}), 400

    return jsonify([Chat.toJSON() for Chat in chats_creador]), 200
    
# Get method: get all messages from a chat
@module_chat_v1.route('/Message/', methods=['GET'])
# RECIBE:
    # GET HTTP request con el id del chat en question
#DEVUELVE
    # -202: Un objeto JSON con todos los mensajes del chat solicitado
    # -400: Un objeto Json con el posible mensaje de error, chat no existe
def open_session():

    if 'participant_id' not in request.json:
        return jsonify({'error_message': 'Participant id attribute missing in json'}), 400
    if 'event_id' not in request.json:
        return jsonify({'error_message': 'Event id attribute missing in json'}), 400

    Participant_id = request.json['participant_id']
    Event_id = request.json['event_id']
    
    try:
        Chat_buscat= Chat.query.filter_by(participant_id = Participant_id, event_id = Event_id).first()
    except:
        return jsonify({"error message": "Algo ha pasado buscando el chat"}), 400
    
    if Chat_buscat is None:
        return jsonify({"error message": "No hay ningun chat con esas credenciales"}), 400

    try:
        messages = Message.query.filter_by(chat_id = Chat_buscat.id)
    except:
        return jsonify({"error message": "Algo ha pasado buscando los mensajes"}), 400

    return jsonify([Resultats.toJSON() for Resultats in messages]), 200