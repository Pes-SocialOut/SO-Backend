# Import flask dependencies
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
import uuid

# Import the database object from the main app module
from app import db

# Import module models
from app.module_admin.models import Admin

# Import utility functions
from app.module_admin.utils import isAdmin

# Define the blueprint: 'admin', set its url prefix: app.url/admin
module_admin_v1 = Blueprint('admin', __name__, url_prefix='/v1/admin')

@module_admin_v1.route('/', methods=['GET'])
@jwt_required(optional=False)
def access():
    auth_id = get_jwt_identity()
    if isAdmin(auth_id):
        return 'Success', 200
    return 'Forbidden', 403