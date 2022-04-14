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
from app.module_event.controllers import module_event_v1
from app.module_airservice.controllers import module_airservice_v1

@app.errorhandler(404)
def not_found(error):
    return "<h1>404</h1><p>This route does not exist on our API, try again ;)</p>", 404

@app.route('/', methods=['GET'])
def homepage():
    return "Home route", 200

# Register blueprint(s)
app.register_blueprint(module_event_v1)
app.register_blueprint(module_airservice_v1)