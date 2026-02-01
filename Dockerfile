FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8000

# Gunicorn serving the Flask app factory output
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app.wsgi:app"]
