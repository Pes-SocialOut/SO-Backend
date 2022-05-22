from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
import string
import random
import subprocess
import os
from datetime import datetime, timedelta
from app.module_airservice.jobs.data_extraction import main as data_extraction
from app.module_airservice.jobs.triangulation import main as triangulation
module_airservice_jobs = Blueprint('air_jobs', __name__, url_prefix='/v1/air/jobs')


@module_airservice_jobs.route('/auth', methods=['GET'])
def get_auth_for_jobs():
    rand_string = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
    access_token = create_access_token(identity=rand_string, expires_delta=timedelta(seconds=10))
    return jsonify({'str': rand_string, 'token': access_token})

@module_airservice_jobs.route('/extract', methods=['GET'])
@jwt_required(optional=False)
def extract_data_from_api_job():
    if 'auth' not in request.args: 
        return 'Forbidden', 403
    if not check_encrypted_passphrase(get_jwt_identity(), request.args['auth']):
        return 'Auth failed', 403
    
    ini_time = datetime.now()
    try:
        data_extraction(os.getenv("DATABASE_URL"))
    except Exception as e:
        return str(e), 400
    delta = datetime.now() - ini_time

    return f'Data extracted in {delta.seconds} seconds\n', 200

@module_airservice_jobs.route('/triangulate', methods=['GET'])
@jwt_required(optional=False)
def calculate_triangulation_job():
    if 'auth' not in request.args: 
        return 'Forbidden', 403
    if not check_encrypted_passphrase(get_jwt_identity(), request.args['auth']):
        return 'Auth failed', 403
    
    ini_time = datetime.now()
    try:
        triangulation(os.getenv("DATABASE_URL"))
    except Exception as e:
        return str(e), 400
    delta = datetime.now() - ini_time

    return f'Triangulation calulated in {delta.seconds} seconds\n', 200

def check_encrypted_passphrase(token_str, encrypted_str):
    secret_key = os.getenv('AIRSERVICE_JOBS_SECRET_KEY')
    sub = subprocess.Popen(f'echo {encrypted_str} | openssl aes-256-cbc -d -a -pass pass:{secret_key} -iter 20', shell=True, stdout=subprocess.PIPE)
    decrypted_str = sub.stdout.read().decode('utf-8').strip()
    if token_str != decrypted_str:
        return False
    return True
