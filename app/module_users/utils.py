from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
# Import module models
from app.module_users.models import User, SocialOutAuth, GoogleAuth, FacebookAuth, EmailVerificationPendant, Achievement, AchievementProgress
from app.utils.email import send_email
import string
import random
from app import db
from datetime import datetime, timedelta, timezone

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
        db_verification = EmailVerificationPendant(email, code, datetime.now(timezone.utc)+timedelta(minutes=15))
        db_verification.save()
    else:
        db_verification.code = code
        db_verification.expires_at = datetime.now(timezone.utc)+timedelta(minutes=15)
        db.session.commit()
    send_email(email, 'SocialOut auth verification code', f'Your verification code for SocialOut authentication is {code}. It expires in 15 minutes.')

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

def increment_achievement_of_user(ach, user):
    ach_updated = False
    achievement_progress = AchievementProgress.query.filter_by(achievement = ach).filter_by(user = user).first()
    if achievement_progress == None:
        achievement_progress = AchievementProgress(user, ach, 1, None)
        ach_updated = True
    else:
        achievement_template = Achievement.query.filter_by(achievement = ach).first()
        if achievement_progress.progress < achievement_template.stages:
            ach_updated = True
            achievement_progress.progress += 1
            if achievement_progress.progress == achievement_template.stages:
                achievement_progress.completed_at = datetime.now()
    if ach_updated:
        achievement_progress.save()