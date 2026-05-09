FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "main:app", "-b", "0.0.0.0:8080"]