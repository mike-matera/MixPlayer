#!/usr/bin/env bash

. ./env/bin/activate

export FLASK_APP=main
export FLASK_ENV=development
export GOOGLE_APPLICATION_CREDENTIALS=./secrets/google-app-creds.json

flask run --host=0.0.0.0
