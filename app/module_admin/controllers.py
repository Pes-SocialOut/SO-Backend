# Import flask dependencies
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import uuid

# Import the database object from the main app module
from app import db, hashing

# Import module models
from app.module_admin.models import Admin
from app.module_users.models import User, SocialOutAuth
from app.module_users.utils import generate_tokens

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