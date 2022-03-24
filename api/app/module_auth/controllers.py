# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import the database object from the main app module
from app import db

# Import module models (i.e. User)
from app.module_auth.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
module_auth = Blueprint('auth', __name__, url_prefix='/auth')

# Set the route and accepted methods
@module_auth.route('/register/<email>', methods=['GET', 'POST'])
def register(email):
    # Create new user
    usr = User("TestUser", email, "myPassword")
    usr.role = 1
    usr.status = 1
    db.session.add(usr)
    db.session.commit()

    # Query users
    result = User.query.filter_by(name="TestUser").all()

    return "Users with name TestUser: " + str(len(result)), 200