#!/bin/bash

export FLASK_ENV=production

# gunicorn wsgi:app -w 1 -b 0:4000 -k eventlet
gunicorn wsgi:app -w 3 -b unix:/tmp/ubattery.sock -k eventlet
