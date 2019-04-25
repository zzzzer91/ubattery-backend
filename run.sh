#!/bin/bash

export FLASK_ENV=production

gunicorn wsgi:app -w 1 -b 0:4000 -k eventlet
