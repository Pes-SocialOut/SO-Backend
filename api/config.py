#TEMPLATE TAKEN FROM DIGITAL_OCEAN PROJECT STRUCTURE
import os

# Statement for enabling the development environment
DEBUG = os.getenv('API_DEBUG')

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database we are working with 
SQLALCHEMY_DATABASE_URI = "postgresql://socialout:password1@localhost:5432/socialout" #os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

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