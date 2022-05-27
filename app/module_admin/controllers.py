# Import flask dependencies
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import uuid

# Import the database object from the main app module
from app import db, hashing

# Import module models
from app.module_admin.models import Admin
from app.module_users.models import BannedEmails, User, SocialOutAuth
from app.module_users.utils import generate_tokens
from app.utils.email import send_email

# Define the blueprint: 'admin', set its url prefix: app.url/admin
module_admin_v1 = Blueprint('admin', __name__, url_prefix='/v1/admin')

@module_admin_v1.route('/', methods=['GET'])
@jwt_required(optional=False)
def access():
    auth_id = get_jwt_identity()
    if Admin.exists(auth_id):
        return 'Success', 200
    return 'Forbidden', 403

@module_admin_v1.route('/login', methods=['POST'])
def login():
    if not ('email' in  request.json and 'password' in request.json):
        return jsonify({'error_message': 'Missing credentials in json body.'}), 400 
    email = request.json['email']
    password = request.json['password']
    user = User.query.filter_by(email = email).first()
    if user == None:
        return jsonify({'error_message': 'Email or password are wrong.'}), 404
    if not Admin.exists(user.id):
        return jsonify({'error_message': 'Only administrators can access this resource.'}), 403
    socialout_auth = SocialOutAuth.query.filter_by(id = user.id).first()
    if socialout_auth == None:
        return jsonify({'error_message': 'Authentication method not available for this email.'}), 400 
    if not hashing.check_value(socialout_auth.pw, password, salt=socialout_auth.salt):
        return jsonify({'error_message': 'Email or password are wrong.'}), 400 
    return generate_tokens(str(user.id)), 200


@module_admin_v1.route('/unban', methods=['POST'])
@jwt_required(optional=False)
def unban():
    auth_id = get_jwt_identity()
    if not Admin.exists(auth_id):
        return jsonify({'error_message': 'Only administrators can make this action.'}), 403
    if not (request.json and 'email' in request.json):
        return jsonify({'error_message': 'Missing email in json body.'}), 400
    
    email = request.json['email']
    reason = request.json['reason']

    ban = BannedEmails.query.filer_by(email = email).first()
    if ban == None:
        return jsonify({'error_message': 'This email is not in the banned emails list.'}), 404

    ban_reason = ban.reason
    ban.delete()

    email_body = 'Hey there! Welcome back to SocialOut.\n\nYou have been unbaned by one of our staff members, \
        please behave properly this time and do not repeat your past mistakes.\n\n'
    if ban_reason != None:
        email_body += f'We remind you the reason you were banned for: {ban_reason}\n\n'
    if reason != None:
        email_body += f'This is the reason for your unban: {reason}\n\n'
    email_body += 'See you around!\nSocialOut team.'
    send_email(email, 'Unban from SocialOut notice.', email_body)
    return jsonify({'success': True}), 200