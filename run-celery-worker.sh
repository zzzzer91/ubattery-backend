#!/bin/bash

celery -A celery_worker.celery worker --loglevel=INFO --concurrency=4