# Import flask and template operators
from flask import Flask
# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
# Import JWT
from flask_jwt_extended import JWTManager
# Import hashing
from flask_hashing import Hashing

# Define the WSGI application object
app = Flask(__name__, static_url_path='/')

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Define the jwt manager for authentication
jwt = JWTManager(app)

# Define the hashing object for app
hashing = Hashing(app)

# Sample HTTP error handling
from app.module_users.controllers import module_users_v1
from app.module_users.controllers_v2 import module_users_v2
from app.module_event.controllers import module_event_v1
from app.module_event.controllers_v2 import module_event_v2
from app.module_event.controllers_v3 import module_event_v3
from app.module_airservice.controllers import module_airservice_v1
from app.module_airservice.jobs.controllers import module_airservice_jobs
from app.module_admin.controllers import module_admin_v1
from app.module_chat.controllers import module_chat_v1

@app.errorhandler(404)
def not_found(error):
    return "<h1>404</h1><p>This route does not exist on our API, try again ;)</p>", 404

@app.route('/', methods=['GET'])
def homepage():
    return "Home route", 200

# Register blueprint(s)
app.register_blueprint(module_users_v1)
app.register_blueprint(module_users_v2)
app.register_blueprint(module_event_v1)
app.register_blueprint(module_event_v2)
app.register_blueprint(module_event_v3)
app.register_blueprint(module_airservice_v1)
app.register_blueprint(module_airservice_jobs)
app.register_blueprint(module_admin_v1)
app.register_blueprint(module_chat_v1)
