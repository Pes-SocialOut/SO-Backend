# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import the database object from the main app module
#from app import db

# Import module models (i.e. User)
#from app.module_auth.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
module_auth = Blueprint('auth', __name__, url_prefix='/auth')

# Set the route and accepted methods
@module_auth.route('/signin/', methods=['GET', 'POST'])
def signin():

    # TODO: Authenticate user

    return "Always successful", 200