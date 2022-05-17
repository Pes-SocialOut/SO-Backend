# Import flask dependencies
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import uuid

# Import the database object from the main app module
from app import db

# Import util functions
from app.utils.email import send_email
from app.module_users.utils import user_id_for_email, authentication_methods_for_user_id, send_verification_code_to, generate_tokens, get_random_salt, verify_password_strength

# Import module models
from app.module_users.models import User, Achievement, AchievementProgress, Friend, UserLanguage, EmailVerificationPendant

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

