# Import flask and template operators
from flask import Flask

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return "This route does not exist on our API, try again ;)", 404

# Import a module / component using its blueprint handler variable (mod_auth)
from app.module_airservice.controllers import module_airservice
#from app.module_domain.controllers import module_domain

# Register blueprint(s)
app.register_blueprint(module_airservice)
#app.register_blueprint(module_domain)

@app.route('/', methods=['GET'])
def homepage():
    return "Home route", 200