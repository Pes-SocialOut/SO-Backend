# Import flask dependencies
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required

# Import the database object from the main app module
from app import db

# Import the hashing object from the main app module
from app import hashing
import string
import random

# Import module models
from app.module_users.models import User, SocialOutAuth, GoogleAuth, FacebookAuth

# Define the blueprint: 'users', set its url prefix: app.url/users
module_users_v1 = Blueprint('users', __name__, url_prefix='/v1/users')

# Endpoints related to profile

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

@module_users_v1.route('/<id>', methods=['PUT'])
def update_profile(id):
    return jsonify({"id": id}), 200

# Endpoints related authentication

@module_users_v1.route("/login/socialout", methods=["POST"])
def login_socialout():
    if not ('email' in  request.json or 'password' in request.json):
        return jsonify({"error_message": "Missing credentials in json body."}), 400 
    email = request.json.email
    password = request.json.password
    user = SocialOutAuth.query.filter_by(email = email).first()
    if user == None:
        return jsonify({"error_message": "Email or password are wrong."}), 400 
    socialout_auth = SocialOutAuth.query.filter_by(id = user.id).first()
    if socialout_auth == None:
        return jsonify({"error_message": "Authentication method not available for this email"}), 400 
    if not hashing.check_value(socialout_auth.pw, password, salt=socialout_auth.salt):
        return jsonify({"error_message": "Email or password are wrong."}), 400 
    return generate_tokens()

@module_users_v1.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)

@module_users_v1.route('/<id>/pw', methods=['POST'])
def change_password(id):
    return jsonify({"id": id}), 200

# Util functions
def generate_tokens(user_id):
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    return jsonify(access_token=access_token, refresh_token=refresh_token)

def get_random_salt(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# jwt_required(optional=False)