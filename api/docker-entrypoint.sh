#!/bin/bash

cd /api

python3 manage.py db migrate
python3 manage.py db upgrade

echo should_have_upgraded_db