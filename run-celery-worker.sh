#!/bin/bash

celery -A ubattery.extensions.celery worker --loglevel=INFO --concurrency=4