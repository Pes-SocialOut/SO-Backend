# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import the database object from the main app module
#from app import db

# Import module models (i.e. User)
from app.module_domain.models_simple import SocialMedia

# Define the blueprint: 'auth', set its url prefix: app.url/auth
module_domain = Blueprint('domain', __name__, url_prefix='/domain')

# Set the route and accepted methods
@module_domain.route('/air_station/', methods=['GET'])
def signin():

    # TODO: Authenticate user

    return 'My awesome airstation', 200