# Import flask dependencies
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import os
import uuid

# Import the database object from the main app module
from app import db

# Import util functions
from app.utils.email import send_email
from app.module_users.utils import increment_achievement_of_user, user_id_for_email, authentication_methods_for_user_id, send_verification_code_to, generate_tokens, get_random_salt, verify_password_strength

# Import module models
from app.module_users.models import FriendInvite, User, Achievement, AchievementProgress, Friend, UserLanguage, EmailVerificationPendant, SocialOutAuth

# Import the hashing object from the main app module
from app import hashing

from datetime import datetime, timedelta, timezone

# Define the blueprint: 'users', set its url prefix: app.url/users
module_users_v2 = Blueprint('users_v2', __name__, url_prefix='/v2/users')


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
        friends = Friend.getFriendsOfUserId(user_id)
        profile['friends'] = [{'id': f.id, 'username': f.username} for f in friends]
        profile['auth_methods'] = authentication_methods_for_user_id(user_id)
    else:
        del profile['email']
    
    profile['achievements'] = Achievement.getAchievementsOfUserId(user_id)
    
    user_languages = UserLanguage.query.filter_by(user = user_id).all()
    profile['languages'] = [ str(l.language.value) for l in user_languages ]
    return jsonify(profile), 200


@module_users_v2.route('/forgot_pw', methods=['GET'])
def send_password_reset_code():
    if not (request.args and 'email' in request.args):
        return jsonify({'error_message': 'Must indicate an email'}), 400
    email = request.args['email']
    user_id = user_id_for_email(email)

    if user_id == None:
        return jsonify({'action': 'error', 'error_message': 'No user found for this email'}), 404

    auth_methods = authentication_methods_for_user_id(user_id)
    if 'socialout' not in auth_methods:
        return jsonify({'action': 'no_auth', 'alternative_auths': auth_methods}), 202
        
    code = get_random_salt(6)
    # Save code to database
    db_verification = EmailVerificationPendant.query.filter_by(email = email).first()
    if db_verification == None:
        db_verification = EmailVerificationPendant(email, code, datetime.now(timezone.utc)+timedelta(minutes=15))
        db_verification.save()
    else:
        db_verification.code = code
        db_verification.expires_at = datetime.now(timezone.utc)+timedelta(minutes=15)
        db.session.commit()
    send_email(email, 'SocialOut: Reset your password with this code.', f'Your verification code for SocialOut password reset is {code}. It expires in 15 minutes.')

    return jsonify({'action': 'continue'}), 200

@module_users_v2.route('/forgot_pw', methods=['POST'])
def reset_forgotten_password():
    if not request.json:
        return jsonify({'error_message': 'Missing json object'}), 400 
    if 'email' not in request.json:
        return jsonify({'error_message': 'Email attribute missing in json'}), 400 
    if 'password' not in request.json:
        return jsonify({'error_message': 'Password attribute missing in json'}), 400 
    if 'verification' not in request.json:
        return jsonify({'error_message': 'Verification code attribute missing in json'}), 400 

    email = request.json['email']
    pw = request.json['password']
    verification = request.json['verification']
    user_id = user_id_for_email(email)

    if user_id == None:
        return jsonify({'error_message': 'No user found for this email'}), 404

     # Check password strength
    pw_msg, pw_status = verify_password_strength(pw)
    if pw_status != 200: return pw_msg, pw_status

    # Check verification code in codes sent to email
    db_verification = EmailVerificationPendant.query.filter(EmailVerificationPendant.email == email).filter(EmailVerificationPendant.expires_at > datetime.now(timezone.utc)).first()
    if db_verification == None:
        return jsonify({'error_message': 'Verification code was never sent to this email or the code has expired.'}), 403
    if db_verification.code != verification:
        return jsonify({'error_message': 'Verification code does not coincide with code sent to email'}), 403
    
    socialout_auth = SocialOutAuth.query.filter(SocialOutAuth.id == user_id).first()

    # Update socialout auth method to user
    user_salt = get_random_salt(15)
    hashed_pw = hashing.hash_value(pw, salt=user_salt)
    socialout_auth.salt = user_salt
    socialout_auth.pw = hashed_pw
    try:
        socialout_auth.save()
    except:
        return jsonify({'error_message': 'Something went wrong when adding auth method socialout to user.'}), 500

    # Remove verification code -> already used
    db_verification.delete()
    
    return generate_tokens(str(user_id)), 200

@module_users_v2.route('/friend_link', methods=['GET'])
@jwt_required(optional=False)
def request_new_friend_link():
    auth_id = uuid.UUID(get_jwt_identity())

    user_invites = FriendInvite.query.filter_by(invitee = auth_id).filter(FriendInvite.expires_at > datetime.now(timezone.utc)).all()
    if len(user_invites) >= 5:
        return jsonify({'error_message': f'You already have {len(user_invites)} invitation links active.'}), 409

    code = get_random_salt(15)
    exp_date = datetime.now()+timedelta(days=3)
    new_invite = FriendInvite(auth_id, code, exp_date)
    try:
        new_invite.save()
    except Exception as e:
        return jsonify({"error_message": f"Something went wrong inserting new invitation code to DB: {code}"}), 500

    link = os.getenv('API_DOMAIN_NAME') + f'/v2/users/new_friend?code={code}'
    return jsonify({'invite_link': link}), 200

@module_users_v2.route('/new_friend', methods=['GET'])
@jwt_required(optional=False)
def accept_friend_link():
    if not (request.args and 'code' in request.args):
        return jsonify({"error_message": "Missing argument code"}), 400

    code = request.args['code']

    auth_id = uuid.UUID(get_jwt_identity())
    
    invitation = FriendInvite.query.filter_by(code = code).filter(FriendInvite.expires_at > datetime.now(timezone.utc)).first()
    if invitation == None:
        return jsonify({"error_message": "Code does not exist or it has expired"}), 404
    
    if invitation.invitee == auth_id:
        return jsonify({"error_message": "Can't add yourself as your frind, but you dou have high self esteem."}), 400
    
    if invitation.invitee in [user.id for user in Friend.getFriendsOfUserId(auth_id)]:
        return jsonify({"error_message": "You are already friends with this user"}), 409
    
    friendship = Friend(invitation.invitee, auth_id)
    friendship.save()

    # Increment achievement
    increment_achievement_of_user('ambassador', invitation.invitee)

    invitation.delete()
    return get_profile(str(invitation.invitee))