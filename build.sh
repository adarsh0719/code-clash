#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Load initial data
python manage.py loaddata initial_data.json