# Import flask dependencies
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
from flask_jwt_extended import get_jwt_identity, jwt_required
import sqlalchemy as db
from sqlalchemy import create_engine
import uuid

from app.module_event.controllers_v3 import delete_event

# Import the database object from the main app module
from app import hashing

# Import module models
from app.module_admin.models import Admin
from app.module_users.models import AchievementProgress, BannedEmails, FacebookAuth, Friend, FriendInvite, GoogleAuth, User, SocialOutAuth, UserLanguage
from app.module_users.utils import generate_tokens
from app.utils.email import send_email
from app.module_event.models import Event
from app.module_chat.controllers import borrar_mensajes_usuario

# Define the blueprint: 'admin', set its url prefix: app.url/v1/admin
module_admin_v1 = Blueprint('admin', __name__, url_prefix='/v1/admin')

@module_admin_v1.route('/login', methods=['POST'])
def login():
    if not ('email' in  request.json and 'password' in request.json):
        return jsonify({'error_message': 'Missing credentials in json body.'}), 400 
    email = request.json['email']
    password = request.json['password']
    user = User.query.filter_by(email = email).first()
    if user == None:
        return jsonify({'error_message': 'Email or password are wrong.'}), 404
    if not Admin.exists(user.id):
        return jsonify({'error_message': 'Only administrators can access this resource.'}), 403
    socialout_auth = SocialOutAuth.query.filter_by(id = user.id).first()
    if socialout_auth == None:
        return jsonify({'error_message': 'Authentication method not available for this email.'}), 400 
    if not hashing.check_value(socialout_auth.pw, password, salt=socialout_auth.salt):
        return jsonify({'error_message': 'Email or password are wrong.'}), 400 
    return generate_tokens(str(user.id)), 200


# LISTAR TODOS LOS EVENTOS REPORTADOS DE TODOS LOS USUARIOS: obtener una lista de, por cada usuario, todos sus eventos reportados
@module_admin_v1.route('/reported', methods=['GET'])
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON con los usuarios y, en cada uno, sus eventos reportados 
@jwt_required(optional=False)
def get_reported_events():
    
    # Ver si el token es de un admin
    auth_id = get_jwt_identity()
    if not Admin.exists(auth_id):
        return jsonify({"error_message": "You're not an admin ;)"}), 400

    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    engine = create_engine(db_uri)
    sql_query = db.text("SELECT events.user_creator, users.username, events.id, events.name, events.date_started , events.date_end, events.max_participants, COUNT(*) AS num_reports FROM events LEFT JOIN users ON events.user_creator = users.id LEFT JOIN review ON events.id = review.event_id WHERE review.rating = 0 GROUP BY events.user_creator, users.username, events.id, events.name, events.date_started , events.date_end, events.max_participants ORDER by num_reports DESC;")
    with engine.connect() as conn:
        result_as_list = conn.execute(sql_query).fetchall()    
    
    data_events = []
    for result in result_as_list:
        data_events.append(dataToJSON(result))
    
    for u1 in data_events:
        events_of_a_user = []
        event_user = [u1["user_id"], u1["user_username"]]
        for u2 in data_events:
            if u1["user_id"] == u2["user_id"]:
                events_of_a_user.append(u2["reported_event"])
        
    definitive = eventJSON(event_user, events_of_a_user)

    return jsonify(definitive), 200


def dataToJSON(data):
    return {
        "user_id": data[0],
        "user_username": data[1],
        "reported_event": {
            "event_id": data[2],
            "event_name": data[3],
            "event_date_started": data[4],
            "event_date_end": data[5],
            "event_max_participants": data[6],
            "event_num_reports": data[7],
        }
    }

def eventJSON(data, events):
    return {
        "id": data[0],
        "username": data[1],
        "reported_event": events
    }


@module_admin_v1.route('/ban', methods=['POST'])
@jwt_required(optional=False)
def ban():
    auth_id = get_jwt_identity()
    if not Admin.exists(auth_id):
        return jsonify({'error_message': 'Only administrators can make this action.'}), 403
    if not (request.json and 'id' in request.json):
        return jsonify({'error_message': 'Missing id in json body.'}), 400
    
    try:
        user_id = uuid.UUID(request.json['id'])
    except:
        return jsonify({"error_message": "id isn't a valid UUID"}), 400
    if Admin.exists(user_id):
        return jsonify({'error_message': 'An administrator user cannot be banned by another administrator user, please contact a higher clearence member.'}), 409
    banned_user = User.query.filter_by(id = user_id).first()
    if banned_user == None:
        return jsonify({'error_message': 'No such user.'}), 404
    ban_reason = None if 'reason' not in request.json else request.json['reason']
    current_time = datetime.now()

    _, status = borrar_mensajes_usuario(user_id)
    if status != 202:
        return jsonify({'error_message': 'Chats cannot be successfully deleted.'}), 500

    # Buscar los eventos del banned_user
    all_events = Event.query.filter_by(user_creator = banned_user.id).all()
    for event in all_events:
        # Si el evento era futuro, notificar participantes de que el evento es cancelado.
        if current_time < event.date_started:
            event_date_str = event.date_started.strftime('%Y-%m-%d')
            for participant in event.participants_in_event:
                if participant.id != banned_user.id:
                    send_email(participant.email, 'Event cacellation!', f'We are sorry to inform you that the event titled "{event.name}" that was scheduled for {event_date_str} has been cacelled.\n\nYours sincerely,\nThe SocialOut team.')
        delete_event(event.id)
    
    # Notificar baneo a usuario
    email_body = 'Due to an accumulation of bad reviews that have been determined to be sufficient to take action we feel obligated to ban you from the SocialOut platform.\n'
    if ban_reason != None:
        email_body += f'\nFurther explanation follows:\n{ban_reason}\n'
    email_body += f'\nIf you feel like this decision is unjustified contact us directly. Your account will be terminated permanently but your email can be removed from our blacklist in the future.\n\nThe SocialOut team.'
    send_email(banned_user.email, 'You have been banned from SocialOut', email_body)

    # Eliminar métodos de autenticación del usuario baneado
    so_auth = SocialOutAuth.query.filter_by(id = banned_user.id).first()
    if so_auth != None:
        so_auth.delete()
    g_auth = GoogleAuth.query.filter_by(id = banned_user.id).first()
    if g_auth != None:
        g_auth.delete()
    f_auth = FacebookAuth.query.filter_by(id = banned_user.id).first()
    if f_auth != None:
        f_auth.delete()
    
    # Eliminar logros del usuario baneado
    ach = AchievementProgress.query.filter_by(user = banned_user.id).all()
    for a in ach:
        a.delete()
    
    # Eliminar amistades del usuario baneado
    friends = Friend.query.filter_by(invitee = banned_user.id).all()
    friends.extend(Friend.query.filter_by(invited = banned_user.id).all())
    for f in friends:
        f.delete()
    invites = FriendInvite.query.filter_by(invitee = banned_user.id).all()
    for i in invites:
        i.delete()
    
    # Eliminar relación idiomas de usuario
    lang = UserLanguage.query.filter_by(user = banned_user.id).all()
    for l in lang:
        l.delete()
    
    # Eliminar usuario
    email_to_ban = banned_user.email
    username_to_ban = banned_user.username
    try:
        banned_user.delete()
    except Exception as e:
        return jsonify({'error_message': 'Error while deleting user instance', 'details': e}), 500
    
    # Añadir usuario a la tabla de baneos
    if BannedEmails.exists(email_to_ban):
        return jsonify({'error_message': 'User email already banned.'}), 200
    ban_instance = BannedEmails(email_to_ban, username_to_ban, current_time, ban_reason)
    ban_instance.save()
    return jsonify({'message': 'User email banned.'}), 201



@module_admin_v1.route('/unban', methods=['POST'])
@jwt_required(optional=False)
def unban():
    auth_id = get_jwt_identity()
    if not Admin.exists(auth_id):
        return jsonify({'error_message': 'Only administrators can make this action.'}), 403
    if not (request.json and 'email' in request.json):
        return jsonify({'error_message': 'Missing email in json body.'}), 400
    
    email = request.json['email']
    reason = request.json['reason']

    ban = BannedEmails.query.filter_by(email = email).first()
    if ban == None:
        return jsonify({'error_message': 'This email is not in the banned emails list.'}), 404

    ban_reason = ban.reason
    ban.delete()

    email_body = 'Hey there! Welcome back to SocialOut.\n\nYou have been unbaned by one of our staff members, \
        please behave properly this time and do not repeat your past mistakes.\n\n'
    if ban_reason != None:
        email_body += f'We remind you the reason you were banned for: {ban_reason}\n\n'
    if reason != None:
        email_body += f'This is the reason for your unban: {reason}\n\n'
    email_body += 'See you around!\nThe SocialOut team.'
    send_email(email, 'Unban from SocialOut notice.', email_body)
    return jsonify({'message': 'Email unbaned'}), 200
