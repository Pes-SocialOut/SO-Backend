# Import flask dependencies
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from datetime import datetime, timedelta, timezone
#from google.oauth2 import id_token
#from google.auth.transport import requests
import requests
import uuid

# Import the database object from the main app module
from app import db

# Import the hashing object from the main app module
from app import hashing
import string
import random

# Import mailing libs
import os
import smtplib
from email.message import EmailMessage

# Import module models
from app.module_users.models import User, SocialOutAuth, GoogleAuth, FacebookAuth, EmailVerificationPendant

# Define the blueprint: 'users', set its url prefix: app.url/users
module_users_v1 = Blueprint('users', __name__, url_prefix='/v1/users')


###################################### PROFILE / CREDENTIALS ######################################

@module_users_v1.route('/<id>', methods=['GET'])
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
    profile['profile_img_uri'] = ''
    profile['mini_profile_img_uri'] = ''
    if is_authenticated_id:
        profile['friends'] = []
    else:
        del profile['email']
    return jsonify(profile), 200

@module_users_v1.route('/<id>', methods=['PUT'])
@jwt_required(optional=False)
def update_profile(id):
    auth_id = get_jwt_identity()
    if id != auth_id:
        return jsonify({'error_message': 'Only the owner of the profile can update it'}), 403
    
    if 'username' not in request.json:
        return jsonify({'error_message': 'Username attribute missing in json'}), 400
    if 'description' not in request.json:
        return jsonify({'error_message': 'Description attribute missing in json'}), 400
    if 'languages' not in request.json:
        return jsonify({'error_message': 'Languages list attribute missing in json'}), 400
    if 'hobbies' not in request.json:
        return jsonify({'error_message': 'Hobbies list attribute missing in json'}), 400
    
    username = request.json['username']
    description = request.json['description']
    languages = request.json['languages']
    hobbies = request.json['hobbies']

    user = User.query.filter_by(id = uuid.UUID(id)).first()
    if (user == None):
        return jsonify({'error_message': f'User does not exist for id {id}'}), 404

    user.username = username
    user.description = description
    user.hobbies = hobbies

    try:
        user.save()
    except:
        return jsonify({'error_message': f'An error occured when updating user {id}'}), 500

    # TODO: Update languages, when implemented

    profile = user.toJSON()

    # TODO: add friend list and languages
    profile['friends'] = []

    return jsonify(profile), 200

@module_users_v1.route('/<id>/pw', methods=['POST'])
@jwt_required(optional=False)
def change_password(id):
    if not ('old' in  request.json and 'new' in request.json):
        return jsonify({'error_message': 'Missing old or new password in json body.'}), 400 
    old_pw = request.json['old']
    new_pw = request.json['new']

    # Check new password requirements
    if old_pw == new_pw:
        return jsonify({'error_message': 'Old and new passwords must be different'}), 400
    
    # Check password strength
    pw_msg, pw_status = verify_password_strength(new_pw)
    if pw_status != 200: return pw_msg, pw_status

    auth_id = get_jwt_identity()
    if id != auth_id:
        return jsonify({'error_message': 'Only the owner of the account can change its password'}), 403
    socialout_auth = SocialOutAuth.query.filter_by(id = uuid.UUID(id)).first()
    if socialout_auth == None:
        return jsonify({'error_message': 'Socialout authentication method not available for this user, can not change password'}), 400 
    if not hashing.check_value(socialout_auth.pw, old_pw, salt=socialout_auth.salt):
        return jsonify({'error_message': 'Wrong old password'}), 400

    debug = f'{socialout_auth.salt} - {socialout_auth.pw}'

    # Add socialout auth method to user
    user_salt = get_random_salt(15)
    hashed_pw = hashing.hash_value(new_pw, salt=user_salt)
    socialout_auth.salt = user_salt
    socialout_auth.pw = hashed_pw
    try:
        db.session.commit()
    except:
        return jsonify({'error_message': f'Something went wrong when changing password for user {id}, {user_salt}, {new_pw}, {hashed_pw} .... {debug}'}), 500

    user = User.query().filter_by(id = uuid.UUID(id)).first()
    send_email(user.email, 'SocialOut password change notice!', f'Your password was recently changed, if it was not you, please log into your {user.username} account by clicking on "Forgot password" in the login screen.')
    return generate_tokens(str(user.id)), 200

############################################ REGISTER #############################################

@module_users_v1.route('/register/check', methods=['GET'])
def check_register_status():
    if 'type' not in request.args:
        return jsonify({'error_message': 'Must indicate type of authentication to check {socialout, google, facebook}'}), 400
    type = request.args['type']
    if type == 'socialout':
        return check_register_status_socialout(request.args)
    if type == 'google':
        return check_register_status_google(request.args)
    if type == 'facebook':
        return check_register_status_facebook(request.args)
    return jsonify({'error_message': 'Type of authentication must be one of {socialout, google, facebook}'}), 400

def check_register_status_socialout(args):
    if 'email' not in args:
        return jsonify({'error_message': 'Socialout auth method must indicate an email'}), 400
    email = args['email']
    user_id = user_id_for_email(email)
    if user_id == None:
        send_verification_code_to(email)
        return jsonify({'action': 'continue'}), 200
    # check if it is socialout
    auth_methods = authentication_methods_for_user_id(user_id)
    if 'socialout' in auth_methods:
        return jsonify({'action': 'error', 'error_message': 'User with this email already exists'}), 200
    send_verification_code_to(email)
    return jsonify({'action': 'link_auth', 'alternative_auths': auth_methods}), 200

def check_register_status_google(args):
    if 'token' not in args:
        return jsonify({'error_message': 'Google auth method must indicate a token'}), 400
    token = args['token']
    # Get google email from token
    try:
        idinfo = requests.get(f'https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}')
        #idinfo = id_token.verify_oauth2_token(token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))
        email = idinfo.json()['email']
    except:
        return jsonify({'error_message': 'Google token was invalid'}), 400
    user_id = user_id_for_email(email)
    if user_id == None:
        return jsonify({'action': 'continue'}), 200
    # check if it is google
    auth_methods = authentication_methods_for_user_id(user_id)
    if 'google' in auth_methods:
        return jsonify({'action': 'error', 'error_message': 'User with this email already exists'}), 200
    return jsonify({'action': 'link_auth', 'alternative_auths': auth_methods}), 200

def check_register_status_facebook(args):
    if 'token' not in args:
        return jsonify({'error_message': 'Google auth method must indicate a token'}), 400
    token = args['token']
    # Get email from facebook token
    try:
        idinfo = requests.get(f'https://graph.facebook.com/me?fields=email&access_token={token}')
        email = idinfo.json()['email']
    except:
        return jsonify({'error_message': 'Facebook token was invalid'}), 400
    user_id = user_id_for_email(email)
    if user_id == None:
        return jsonify({'action': 'continue'}), 200
    # check if it is google
    auth_methods = authentication_methods_for_user_id(user_id)
    if 'facebook' in auth_methods:
        return jsonify({'action': 'error', 'error_message': 'User with this email already exists'}), 200
    return jsonify({'action': 'link_auth', 'alternative_auths': auth_methods}), 200


@module_users_v1.route('/register/socialout', methods=['POST'])
def register_socialout():
    if 'email' not in request.json:
        return jsonify({'error_message': 'Email attribute missing in json'}), 400 
    if 'password' not in request.json:
        return jsonify({'error_message': 'Password attribute missing in json'}), 400 
    if 'username' not in request.json:
        return jsonify({'error_message': 'Username attribute missing in json'}), 400 
    if 'description' not in request.json:
        return jsonify({'error_message': 'Description attribute missing in json'}), 400 
    if 'languages' not in request.json:
        return jsonify({'error_message': 'Languages list attribute missing in json'}), 400 
    if 'hobbies' not in request.json:
        return jsonify({'error_message': 'Hobbies list attribute missing in json'}), 400 
    if 'verification' not in request.json:
        return jsonify({'error_message': 'Verification code attribute missing in json'}), 400 
    
    email = request.json['email']
    pw = request.json['password']
    username = request.json['username']
    description = request.json['description']
    languages = request.json['languages']
    hobbies = request.json['hobbies']
    verification = request.json['verification']

    # Check no other user exists with that email
    if user_id_for_email(email) != None:
        return jsonify({'error_message': 'User with this email already exists'}), 400
    
    # Check password strength
    pw_msg, pw_status = verify_password_strength(pw)
    if pw_status != 200: return pw_msg, pw_status

    # Check verification code in codes sent to email
    db_verification = EmailVerificationPendant.query.filter_by(email = email).first()
    if db_verification == None:
        return jsonify({'error_message': 'Verification code was never sent to this email.'}), 400
    if db_verification.code != verification:
        return jsonify({'error_message': 'Verification code does not coincide with code sent to email'}), 400

    # Add user to bd
    user_id = uuid.uuid4()
    user = User(user_id, username, email, description, hobbies)
    try:
        user.save()
    except:
        return jsonify({'error_message': 'Something went wrong when creating new user in db'}), 500
    
    # Add languages to user (once implemented)
    
    # Add socialout auth method to user
    user_salt = get_random_salt(15)
    hashed_pw = hashing.hash_value(pw, salt=user_salt)
    socialout_auth = SocialOutAuth(user_id, user_salt, hashed_pw)
    try:
        socialout_auth.save()
    except:
        return jsonify({'error_message': 'Something went wrong when adding auth method socialout to user'}), 500

    # Remove verification code -> already used
    db_verification.delete()
    
    return generate_tokens(str(user_id)), 200

@module_users_v1.route('/register/google', methods=['POST'])
def register_google():
    if 'token' not in request.json:
        return jsonify({'error_message': 'Token attribute missing in json'}), 400 
    if 'username' not in request.json:
        return jsonify({'error_message': 'Username attribute missing in json'}), 400 
    if 'description' not in request.json:
        return jsonify({'error_message': 'Description attribute missing in json'}), 400 
    if 'languages' not in request.json:
        return jsonify({'error_message': 'Languages list attribute missing in json'}), 400 
    if 'hobbies' not in request.json:
        return jsonify({'error_message': 'Hobbies list attribute missing in json'}), 400
    
    token = request.json['token']
    username = request.json['username']
    description = request.json['description']
    languages = request.json['languages']
    hobbies = request.json['hobbies']

    # Get google email from token
    try:
        idinfo = requests.get(f'https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}')
        #idinfo = id_token.verify_oauth2_token(token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))
        email = idinfo.json()['email']
    except:
        return jsonify({'error_message': 'Google token was invalid'}), 400
    
    # Check no other user exists with that email
    if user_id_for_email(email) != None:
        return jsonify({'error_message': 'User with this email already exists'}), 400

    # Add user to bd
    user_id = uuid.uuid4()
    user = User(user_id, username, email, description, hobbies)
    try:
        user.save()
    except:
        return jsonify({'error_message': 'Something went wrong when creating new user in db'}), 500
    
    # Add languages to user (once implemented)
    
    # Add google auth method to user
    google_auth = GoogleAuth(user_id, token)
    try:
        google_auth.save()
    except:
        return jsonify({'error_message': 'Something went wrong when adding auth method google to user'}), 500
    
    return generate_tokens(str(user_id)), 200

@module_users_v1.route('/register/facebook', methods=['POST'])
def register_facebook():
    if 'token' not in request.json:
        return jsonify({'error_message': 'Token attribute missing in json'}), 400 
    if 'username' not in request.json:
        return jsonify({'error_message': 'Username attribute missing in json'}), 400 
    if 'description' not in request.json:
        return jsonify({'error_message': 'Description attribute missing in json'}), 400 
    if 'languages' not in request.json:
        return jsonify({'error_message': 'Languages list attribute missing in json'}), 400 
    if 'hobbies' not in request.json:
        return jsonify({'error_message': 'Hobbies list attribute missing in json'}), 400
    
    token = request.json['token']
    username = request.json['username']
    description = request.json['description']
    languages = request.json['languages']
    hobbies = request.json['hobbies']

    # Get email from facebook token
    try:
        idinfo = requests.get(f'https://graph.facebook.com/me?fields=email&access_token={token}')
        email = idinfo.json()['email']
    except:
        return jsonify({'error_message': 'Google token was invalid'}), 400
    
    # Check no other user exists with that email
    if user_id_for_email(email) != None:
        return jsonify({'error_message': 'User with this email already exists'}), 400

    # Add user to bd
    user_id = uuid.uuid4()
    user = User(user_id, username, email, description, hobbies)
    try:
        user.save()
    except:
        return jsonify({'error_message': 'Something went wrong when creating new user in db'}), 500
    
    # Add languages to user (once implemented)
    
    # Add facebook auth method to user
    facebook_auth = FacebookAuth(user_id, token)
    try:
        facebook_auth.save()
    except:
        return jsonify({'error_message': 'Something went wrong when adding auth method google to user'}), 500
    
    return generate_tokens(str(user_id)), 200


############################################# LOGIN ###############################################

@module_users_v1.route('/login/check', methods=['GET'])
def check_login_status():
    if 'type' not in request.args:
        return jsonify({'error_message': 'Must indicate type of authentication to check {socialout, google, facebook}'}), 400
    type = request.args['type']
    if type == 'socialout':
        return check_login_status_socialout(request.args)
    if type == 'google':
        return check_login_status_google(request.args)
    if type == 'facebook':
        return check_login_status_facebook(request.args)

    return jsonify({'error_message': 'Type of authentication must be one of {socialout, google, facebook}'}), 400

def check_login_status_socialout(args):
    if 'email' not in args:
        return jsonify({'error_message': 'Socialout auth method must indicate an email'}), 400
    email = args['email']
    user_id = user_id_for_email(email)
    if user_id == None:
        return jsonify({'action': 'error', 'error_message': 'Account does not exist'}), 200
    # check if it is socialout
    auth_methods = authentication_methods_for_user_id(user_id)
    if 'socialout' in auth_methods:
        return jsonify({'action': 'continue'}), 200
    send_verification_code_to(email)
    return jsonify({'action': 'link_auth', 'alternative_auths': auth_methods}), 200

def check_login_status_google(args):
    if 'token' not in args:
        return jsonify({'error_message': 'Google auth method must indicate a token'}), 400
    token = args['token']
    # Get google email from token
    try:
        idinfo = requests.get(f'https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}')
        #idinfo = id_token.verify_oauth2_token(token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))
        email = idinfo.json()['email']
    except:
        return jsonify({'error_message': 'Google token was invalid'}), 400
    user_id = user_id_for_email(email)
    if user_id == None:
        return jsonify({'action': 'error', 'error_message': 'Account does not exist'}), 200
    # check if it is google
    auth_methods = authentication_methods_for_user_id(user_id)
    if 'google' in auth_methods:
        return jsonify({'action': 'continue'}), 200
    return jsonify({'action': 'link_auth', 'alternative_auths': auth_methods}), 200

def check_login_status_facebook(args):
    if 'token' not in args:
        return jsonify({'error_message': 'Facebook auth method must indicate a token'}), 400
    token = args['token']
    # Get email from facebook token
    try:
        idinfo = requests.get(f'https://graph.facebook.com/me?fields=email&access_token={token}')
        email = idinfo.json()['email']
    except:
        return jsonify({'error_message': 'Facebook token was invalid'}), 400
    user_id = user_id_for_email(email)
    if user_id == None:
        return jsonify({'action': 'error', 'error_message': 'Account does not exist'}), 200
    # check if it is facebook
    auth_methods = authentication_methods_for_user_id(user_id)
    if 'facebook' in auth_methods:
        return jsonify({'action': 'continue'}), 200
    return jsonify({'action': 'link_auth', 'alternative_auths': auth_methods}), 200

@module_users_v1.route('/login/socialout', methods=['POST'])
def login_socialout():
    if not ('email' in  request.json and 'password' in request.json):
        return jsonify({'error_message': 'Missing credentials in json body.'}), 400 
    email = request.json['email']
    password = request.json['password']
    user = User.query.filter_by(email = email).first()
    if user == None:
        return jsonify({'error_message': 'Email or password are wrong.'}), 400 
    socialout_auth = SocialOutAuth.query.filter_by(id = user.id).first()
    if socialout_auth == None:
        return jsonify({'error_message': 'Authentication method not available for this email'}), 400 
    if not hashing.check_value(socialout_auth.pw, password, salt=socialout_auth.salt):
        return jsonify({'error_message': 'Email or password are wrong.'}), 400 
    return generate_tokens(str(user.id)), 200

@module_users_v1.route('/login/google', methods=['POST'])
def login_google():
    if 'token' not in request.json:
        return jsonify({'error_message': 'Missing credentials in json body.'}), 400 
    token = request.json['token']
    # Get google email from token
    try:
        idinfo = requests.get(f'https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}')
        #idinfo = id_token.verify_oauth2_token(token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))
        email = idinfo.json()['email']
    except:
        return jsonify({'error_message': 'Google token was invalid'}), 400
    user = User.query.filter_by(email = email).first()
    if user == None:
        return jsonify({'error_message': 'User does not exist'}), 400 
    google_auth = GoogleAuth.query.filter_by(id = user.id).first()
    if google_auth == None:
        return jsonify({'error_message': 'Authentication method not available for this email'}), 400 
    return generate_tokens(str(user.id)), 200

@module_users_v1.route('/login/facebook', methods=['POST'])
def login_facebook():
    if 'token' not in request.json:
        return jsonify({'error_message': 'Missing credentials in json body.'}), 400 
    token = request.json['token']
    # Get email from facebook token
    try:
        idinfo = requests.get(f'https://graph.facebook.com/me?fields=email&access_token={token}')
        email = idinfo.json()['email']
    except:
        return jsonify({'error_message': 'Facebook token was invalid'}), 400
    user = User.query.filter_by(email = email).first()
    if user == None:
        return jsonify({'error_message': 'User does not exist'}), 400 
    facebook_auth = FacebookAuth.query.filter_by(id = user.id).first()
    if facebook_auth == None:
        return jsonify({'error_message': 'Authentication method not available for this email'}), 400 
    return generate_tokens(str(user.id)), 200

@module_users_v1.route('/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    exp_timestamp = get_jwt()["exp"]
    now = datetime.now(timezone.utc)
    target_timestamp = datetime.timestamp(now + timedelta(days=2))
    if target_timestamp > exp_timestamp:
        refresh_token = create_refresh_token(identity=identity)
        return jsonify({'id': identity, 'access_token': access_token, 'refresh_token': refresh_token})
    return jsonify({'id': identity, 'access_token': access_token})


########################################## ADD AUTH METHOD ########################################

@module_users_v1.route('/auth_method', methods=['POST'])
def link_auth_method():
    if 'type' not in request.json:
        return jsonify({'error_message': 'Must indicate type of authentication to link {socialout, google, facebook}'}), 400
    if 'credentials' not in request.json:
        return jsonify({'error_message': 'Missing attribute credentials in json body'}), 400
    type = request.json['type']
    if type == 'socialout':
        return link_socialout_auth_method(request.json['credentials'])
    if type == 'google':
        return link_google_auth_method(request.json['credentials'])
    if type == 'facebook':
        return link_facebook_auth_method(request.json['credentials'])

def link_socialout_auth_method(args):
    if not ('email' in args and 'password' in args and 'verification' in args):
        return jsonify({'error_message': 'Socialout auth method must indicate email, password and verification in credentials'}), 400
    email = args['email']
    password = args['password']
    verification = args['verification']
    user_id = user_id_for_email(email)
    # Check user exists
    if user_id == None:
        return jsonify({'error_message': 'User with this email does not exist, please register first'}), 400

    # Check password strength
    pw_msg, pw_status = verify_password_strength(password)
    if pw_status != 200: return pw_msg, pw_status

    # Check verification code in codes sent to email
    db_verification = EmailVerificationPendant.query.filter_by(email = email).first()
    if db_verification == None:
        return jsonify({'error_message': 'Verification code was never sent to this email.'}), 400
    if db_verification.code != verification:
        return jsonify({'error_message': 'Verification code does not coincide with code sent to email'}), 400
    
    # Add socialout auth method to user
    user_salt = get_random_salt(15)
    hashed_pw = hashing.hash_value(password, salt=user_salt)
    socialout_auth = SocialOutAuth(user_id, user_salt, hashed_pw)
    try:
        socialout_auth.save()
    except:
        return jsonify({'error_message': 'Something went wrong when adding auth method socialout to user'}), 500

    # Remove verification code -> already used
    db_verification.delete()
    
    return generate_tokens(str(user_id)), 200

def link_google_auth_method(args):
    if 'token' not in args:
        return jsonify({'error_message': 'Google auth method must indicate token in credentials'}), 400
    token = args['token']
    # Get google email from token
    try:
        idinfo = requests.get(f'https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}')
        #idinfo = id_token.verify_oauth2_token(token, requests.Request(), os.getenv('GOOGLE_CLIENT_ID'))
        email = idinfo.json()['email']
    except:
        return jsonify({'error_message': 'Google token was invalid'}), 400

    user_id = user_id_for_email(email)
    # Check user exists
    if user_id == None:
        return jsonify({'error_message': 'User with this email does not exist, please register first'}), 400
    
    # Check user does not already have google auth enabled
    google_auth = GoogleAuth.query.filter_by(id = user_id).first()
    if (google_auth != None):
        return jsonify({'error_message': 'Google auth method already linked to this account'}), 400
    
    # Add google auth method to user
    google_auth = GoogleAuth(user_id, token)
    try:
        google_auth.save()
    except:
        return jsonify({'error_message': 'Something went wrong when adding auth method google to user'}), 500
    
    return generate_tokens(str(user_id)), 200

def link_facebook_auth_method(args):
    if 'token' not in args:
        return jsonify({'error_message': 'Facebook auth method must indicate token in credentials'}), 400
    token = args['token']
    # Get google email from token
    try:
        idinfo = requests.get(f'https://graph.facebook.com/me?fields=email&access_token={token}')
        email = idinfo.json()['email']
    except:
        return jsonify({'error_message': 'Facebook token was invalid'}), 400

    user_id = user_id_for_email(email)
    # Check user exists
    if user_id == None:
        return jsonify({'error_message': 'User with this email does not exist, please register first'}), 400
    
    # Check user does not already have google auth enabled
    facebook_auth = FacebookAuth.query.filter_by(id = user_id).first()
    if (facebook_auth != None):
        return jsonify({'error_message': 'Facebook auth method already linked to this account'}), 400
    
    # Add facebook auth method to user
    facebook_auth = FacebookAuth(user_id, token)
    try:
        facebook_auth.save()
    except:
        return jsonify({'error_message': 'Something went wrong when adding auth method google to user'}), 500
    
    return generate_tokens(str(user_id)), 200


######################################### UTILITY FUNCTIONS #######################################

def user_id_for_email(email):
    user = User.query.filter_by(email = email).first()
    if user == None:
        return None
    return user.id

def authentication_methods_for_user_id(id):
    result = []
    socialout_auth = SocialOutAuth.query.filter_by(id = id).first()
    if socialout_auth != None:
        result.append('socialout')
    google_auth = GoogleAuth.query.filter_by(id = id).first()
    if google_auth != None:
        result.append('google')
    fb_auth = FacebookAuth.query.filter_by(id = id).first()
    if fb_auth != None:
        result.append('facebook')
    return result

def send_verification_code_to(email):
    code = get_random_salt(6)
    # Save code to database
    db_verification = EmailVerificationPendant.query.filter_by(email = email).first()
    if db_verification == None:
        db_verification = EmailVerificationPendant(email, code)
        db_verification.save()
    else:
        db_verification.code = code
        db.session.commit()
    send_email(email, 'SocialOut auth verification code', f'Your verification code for SocialOut authentication is {code}')

def send_email(email, subject, body):
    EMAIL_ADRESS = os.getenv('MAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADRESS
    msg['To'] = email
    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def generate_tokens(user_id):
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    return jsonify(id=user_id,access_token=access_token, refresh_token=refresh_token)

def get_random_salt(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def verify_password_strength(pw):
    if len(pw) < 8:
        return jsonify({'error_message': 'New password must have a length of at least 8 characters'}), 400
    if (sum(1 for c in pw if c.isupper()) == 0):
        return jsonify({'error_message': 'New password must have at least one uppercase letter'}), 400
    if (sum(1 for c in pw if c.islower()) == 0):
        return jsonify({'error_message': 'New password must have at least one lowercase letter'}), 400
    if (all([not c.isdigit() for c in pw])):
        return jsonify({'error_message': 'New password must have at least one number digit'}), 400
    return {}, 200
