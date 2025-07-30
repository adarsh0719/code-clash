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

# Expose the port your app runs on
EXPOSE 8000

# Set environment path to use the venv
ENV PATH="/opt/venv/bin:$PATH"

# Start the Django app using gunicorn
CMD ["gunicorn", "dsa_tracker.wsgi:application", "--bind", "0.0.0.0:8000"]
