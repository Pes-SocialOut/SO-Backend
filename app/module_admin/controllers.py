# Import flask dependencies
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.module_event.models import Event, Review
import sqlalchemy as db
from sqlalchemy import create_engine, inspect
import uuid

# Import the database object from the main app module
from app import db, hashing

# Import module models
from app.module_admin.models import Admin
from app.module_users.models import User, SocialOutAuth
from app.module_users.utils import generate_tokens

# Define the blueprint: 'admin', set its url prefix: app.url/admin
module_admin_v1 = Blueprint('admin', __name__, url_prefix='/v1/admin')

@module_admin_v1.route('/', methods=['GET'])
@jwt_required(optional=False)
def access():
    auth_id = get_jwt_identity()
    if Admin.exists(auth_id):
        return 'Success', 200
    return 'Forbidden', 403

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
