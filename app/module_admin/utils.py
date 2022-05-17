import uuid

# Import module models
from app.module_admin.models import Admin

def isAdmin(user_id):
    if type(user_id) == str:
        user_id = uuid.UUID(user_id)
    return Admin.query.filter_by(id = user_id).first() != None