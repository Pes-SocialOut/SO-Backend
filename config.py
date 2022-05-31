#TEMPLATE TAKEN FROM DIGITAL_OCEAN PROJECT STRUCTURE
import os
from datetime import timedelta

# Statement for enabling the development environment
DEBUG = os.getenv('API_DEBUG')

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database we are working with 
SQLALCHEMY_DATABASE_URI = (os.getenv('DATABASE_URL') if os.getenv('DATABASE_URL') is not None else '').replace('postgres://', 'postgresql://')
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

MIGRATIONS_SQLALCHEMY_DATABASE_URI = (os.getenv('DATABASE_URL') if os.getenv('DATABASE_URL') is not None else '').replace('postgres://', 'postgresql://')

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = os.getenv('API_SECRET_KEY')

# Secret key for signing cookies
SECRET_KEY = os.getenv('API_SECRET_KEY')

# JWT related configurations
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# Mail related configurations
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_USE_TLS = False
MAIL_USE_SSL = True
