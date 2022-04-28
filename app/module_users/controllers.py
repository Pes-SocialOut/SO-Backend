# Import flask dependencies
from flask import Blueprint, jsonify, request
import sqlalchemy

# Import the database object from the main app module
from app import db

# Import module models
from app.module_users.models import User, SocialOutAuth, GoogleAuth, FacebookAuth

import uuid

# Define the blueprint: 'users', set its url prefix: app.url/users
module_users_v1 = Blueprint('users', __name__, url_prefix='/v1/users')

@module_users_v1.route('/', methods=['POST'])
def create_user():
    # todo hardcoded
    user_uuid = uuid.uuid4()
    user_username = "manu"
    user_email = "manu@elputoamo.com"
    user_profile_img_uri = "pen"
    user_mini_profile_img_uri = "e"
    user_description = "test"

    user_test = User(user_uuid, user_username, user_email, user_profile_img_uri, user_mini_profile_img_uri, user_description)

    # Errores al guardar en la base de datos: FK violated, etc
    try:
        user_test.save()
    except sqlalchemy.exc.IntegrityError:
        return jsonify({"error_message": "FK violated"})

    return jsonify({"message": "all good"}), 201

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

