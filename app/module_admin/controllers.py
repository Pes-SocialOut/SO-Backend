# Import flask dependencies
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.module_event.models import Event, Review
import sqlalchemy as db
from sqlalchemy import create_engine, inspect
import uuid

# Import the database object from the main app module
from app import db

# Import module models
from app.module_admin.models import Admin

# Import utility functions
from app.module_admin.utils import isAdmin

# Define the blueprint: 'admin', set its url prefix: app.url/admin
module_admin_v1 = Blueprint('admin', __name__, url_prefix='/v1/admin')

@module_admin_v1.route('/', methods=['GET'])
@jwt_required(optional=False)
def access():
    auth_id = get_jwt_identity()
    if isAdmin(auth_id):
        return 'Success', 200
    return 'Forbidden', 403



# LISTAR TODOS LOS EVENTOS REPORTADOS DE TODOS LOS USUARIOS: obtener una lista de, por cada usuario, todos sus eventos reportados
@module_admin_v1.route('/reported', methods=['GET'])
# DEVUELVE:
# - 400: Un objeto JSON con los posibles mensajes de error, id no valida o evento no existe
# - 200: Un objeto JSON con los usuarios y, en cada uno, sus eventos reportados 
@jwt_required(optional=False)
def get_reported_events():
    
    # Ver si el token es de un admin
    # auth_id = get_jwt_identity()
    # if not isAdmin(auth_id):
    #     return jsonify({"error_message": "You're not an admin ;)"}), 400

    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    engine = create_engine(db_uri)
    sql_query = db.text("SELECT events.user_creator, users.username, events.id, events.name, events.date_started , events.date_end, events.max_participants, COUNT(*) AS num_reports FROM events LEFT JOIN users ON events.user_creator = users.id LEFT JOIN review ON events.id = review.event_id WHERE review.rating = 0 GROUP BY events.user_creator, users.username, events.id, events.name, events.date_started , events.date_end, events.max_participants ORDER by num_reports DESC;")
    with engine.connect() as conn:
        result_as_list = conn.execute(sql_query).fetchall()    
    
    data = []
    for result in result_as_list:
        data.append(dataToJSON(result))
    
    return jsonify(data), 200
#    return str(sql_query), 200
    
    #Event.query(Event.user_creator, Event.id, Event.name, Event.date_started, Event.date_end, Event.max_participants, ).join(Review, Review.event_id == Event.id, isouter=True).filter(Review.rating == 0).group_by()

    # queremos, por cada usuario, todos sus eventos reportados POR ORDEN DE CUAL HA SIDO MAS REPORTADO

    # podemos hacer un join de evento y reviews (por id de evento, event_id de review) para conseguir los eventos con reviews = 0
    #
    # SELECT events.user_creator, events.id, events.name, events.date_started , events.date_end, events.max_participants, COUNT(*) AS num_reports
    # FROM events
    # LEFT JOIN review ON events.id = review.event_id
    # WHERE review.rating = 0
    # GROUP BY events.user_creator, events.id, events.name, events.date_started , events.date_end, events.max_participants
    # ORDER by num_reports DESC;

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