# Import flask dependencies
from flask import Blueprint, jsonify, request

# Import the database object from the main app module
from app import db

# Import module models
from app.module_users.models import User, SocialOutAuth, GoogleAuth, FacebookAuth

# Define the blueprint: 'users', set its url prefix: app.url/users
module_users_v1 = Blueprint('users', __name__, url_prefix='/v1/users')

@module_users_v1.route('/<id>', methods=['GET'])
def get_profile(id):
    # hardcoded auth variable
    is_authenticated_id = True
    query_result = User.query.filter_by(id = id).first()
    if query_result == None:
            return jsonify({"error_message":f"User with id {id} does not exist"}), 404
    profile = query_result.toJSON()
    if is_authenticated_id:
        profile["friends"] = []
    else:
        del profile["email"]
    return jsonify(profile), 200

@module_users_v1.route('/<id>', methods=['PATCH'])
def update_profile(id):
    return jsonify({"id": id}), 200

@module_users_v1.route('/<id>/pw', methods=['POST'])
def change_password(id):
    return jsonify({"id": id}), 200
