# Import flask dependencies
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
import uuid

# Import the database object from the main app module
from app import db

# Import the hashing object from the main app module
from app import hashing
import string
import random

# Import module models
from app.module_users.models import User, SocialOutAuth, GoogleAuth, FacebookAuth, EmailVerificationPendant

# Define the blueprint: 'users', set its url prefix: app.url/users
module_users_v1 = Blueprint('users', __name__, url_prefix='/v1/users')

# Endpoints related to profile

@module_users_v1.route('/<id>', methods=['GET'])
@jwt_required(optional=True)
def get_profile(id):
    auth_id = get_jwt_identity()
    is_authenticated_id = id == auth_id
    try:
        user_id = uuid.UUID(id)
    except:
        return jsonify({"error_message": "ID isn't a valid UUID"}), 400
    query_result = User.query.filter_by(id = user_id).first()
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

@module_users_v1.route("/register/socialout", methods=["POST"])
def register_socialout():
    if "email" not in request.json:
        return jsonify({"error_message": "Email attribute missing in json"}), 400 
    if "password" not in request.json:
        return jsonify({"error_message": "Password attribute missing in json"}), 400 
    if "username" not in request.json:
        return jsonify({"error_message": "Username attribute missing in json"}), 400 
    if "description" not in request.json:
        return jsonify({"error_message": "Description attribute missing in json"}), 400 
    if "languages" not in request.json:
        return jsonify({"error_message": "Languages list attribute missing in json"}), 400 
    if "hobbies" not in request.json:
        return jsonify({"error_message": "Hobbies list attribute missing in json"}), 400 
    if "verification" not in request.json:
        return jsonify({"error_message": "Verification code attribute missing in json"}), 400 
    
    email = request.json["email"]
    pw = request.json["password"]
    username = request.json["username"]
    description = request.json["description"]
    languages = request.json["languages"]
    hobbies = request.json["hobbies"]
    verification = request.json["verification"]

    # Check no other user exists with that email
    email_verification = User.query.filter_by(email = email).first()
    if email_verification != None:
        return jsonify({"error_message": "User with this email already exists"}), 400
    
    # Check verification code in codes sent to email
    db_verification = EmailVerificationPendant.query.filter_by(email = email).first()
    if db_verification == None:
        return jsonify({"error_message": "Verification code was never sent to this email."}), 400
    if db_verification.code != verification:
        return jsonify({"error_message": "Verification code does not coincide with code sent to email"}), 400

    # Add user to bd
    user_id = uuid.uuid4()
    user = User(user_id, username, email, None, None, description, hobbies)
    try:
        user.save()
    except:
        return jsonify({"error_message": "Something went wrong when creating new user in db"}), 500
    
    # Add languages to user (once implemented)
    
    # Add socialout auth method to user
    user_salt = get_random_salt(15)
    hashed_pw = hashing.hash_value(pw, salt=user_salt)
    socialout_auth = SocialOutAuth(user_id, user_salt, hashed_pw)
    try:
        socialout_auth.save()
    except:
        return jsonify({"error_message": "Something went wrong when adding auth method socialout to user"}), 500
    
    return generate_tokens(str(user_id))



@module_users_v1.route("/login/socialout", methods=["POST"])
def login_socialout():
    if not ('email' in  request.json or 'password' in request.json):
        return jsonify({"error_message": "Missing credentials in json body."}), 400 
    email = request.json["email"]
    password = request.json["password"]
    user = User.query.filter_by(email = email).first()
    if user == None:
        return jsonify({"error_message": "Email or password are wrong."}), 400 
    socialout_auth = SocialOutAuth.query.filter_by(id = user.id).first()
    if socialout_auth == None:
        return jsonify({"error_message": "Authentication method not available for this email"}), 400 
    if not hashing.check_value(socialout_auth.pw, password, salt=socialout_auth.salt):
        return jsonify({"error_message": "Email or password are wrong."}), 400 
    return generate_tokens(str(user.id))

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