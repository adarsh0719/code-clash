# Use official Python 3.12 image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Create a virtual environment
RUN python -m venv /opt/venv

# Activate venv and install dependencies
RUN /opt/venv/bin/pip install --upgrade pip setuptools wheel
RUN /opt/venv/bin/pip install -r requirements.txt

# Set environment path to use the venv
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port
EXPOSE 8000

# Run migrations, collectstatic, then start Gunicorn
CMD ["sh", "-c", "\
  python manage.py migrate && \
  python manage.py collectstatic --noinput && \
  python manage.py loaddata initial_data.json && \
  echo \"from django.contrib.auth import get_user_model; \
  User = get_user_model(); \
  User.objects.filter(username='admin').exists() or \
  User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')\" | python manage.py shell && \
  gunicorn dsa_tracker.wsgi:application --bind 0.0.0.0:8000"]
