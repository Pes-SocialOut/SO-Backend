# Import flask dependencies
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import uuid

# Import the database object from the main app module
from app import db

# Import module models
from app.module_users.models import User, SocialOutAuth, GoogleAuth, FacebookAuth, EmailVerificationPendant

# Define the blueprint: 'users', set its url prefix: app.url/users
module_users_v2 = Blueprint('users', __name__, url_prefix='/v2/users')


###################################### PROFILE / CREDENTIALS ######################################

@module_users_v2.route('/<id>', methods=['GET'])
@jwt_required(optional=True)
def get_profile(id):
    auth_id = get_jwt_identity()
    is_authenticated_id = id == auth_id
    try:
        user_id = uuid.UUID(id)
    except:
        return jsonify({'error_message': 'ID is not a valid UUID'}), 400
    query_result = User.query.filter_by(id = user_id).first()
    if query_result == None:
            return jsonify({'error_message':f'User with id {id} does not exist'}), 404
    profile = query_result.toJSON()
    if is_authenticated_id:
        profile['friends'] = [] # TODO: add friends
    else:
        del profile['email']
    # Add languages, when implemented
    return jsonify(profile), 200

