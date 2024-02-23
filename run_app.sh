#!/bin/bash
./create_env.sh
source env/bin/activate
uvicorn wsgi:app --reload --host 0.0.0.0 --port 5000 --proxy-headers
#python -m flask --app webapp.py run --debug --host=0.0.0.0 --with-threads