from base64 import b64decode, b64encode
from flask import Flask, abort, request, render_template, jsonify
from redis import Redis
from os import getenv

from helpers import random_string, validate_integer, validate_secret_type, get_and_validate_view_count

APP_HOST = getenv("APP_HOST") or "0.0.0.0"
APP_PORT = getenv("APP_PORT") or "8080"
APP_MAX_DATA_LENGHT = int(getenv("APP_DATA_LENGHT")) if getenv("APP_DATA_LENGHT") else 1024 * 1024
REDIS_HOST = getenv("REDIS_HOST") or "localhost"

rds = Redis(host=REDIS_HOST)
app = Flask(__name__, static_url_path="/static")


@app.route("/")
def index():
    return render_template("save.html"), 200

@app.route("/create-secret", methods=["POST"])
def create_secret():
    secret_json = request.get_json()
    secret_type = secret_json.get("type")
    secret_expire = secret_json.get("expire")
    secret_view_count = secret_json.get("view_count")
    secret_filename = secret_json.get("filename")

    if validate_secret_type(secret_type) and validate_integer(secret_expire) and validate_integer(secret_view_count):
        data = secret_json.get("data")
        key = random_string()
        key_type = f"{key}_type"
        key_view_count = f"{key}_view_count"
        key_filename = f"{key}_filename"
        if data:
            try:
                data = b64decode(data)
            except:
                return jsonify({"status": "error"}), 400
            
            if len(data) <= APP_MAX_DATA_LENGHT:
                rds.setex(key, secret_expire, data)
                rds.setex(key_type, secret_expire, secret_type)
                rds.setex(key_view_count, secret_expire, secret_view_count)
                if secret_filename:
                    rds.setex(key_filename, secret_expire, secret_filename)
                return jsonify({"status": "ok", "key": key}), 200
    
    return jsonify({"status": "error"}), 400

@app.route("/secret/<key>", methods=["GET"])
def get_secret(key):
    key_type = f"{key}_type"
    key_view_count = f"{key}_view_count"
    key_filename = f"{key}_filename"
    status, parsed_integer = get_and_validate_view_count(rds.get(key_view_count))
    if status:
        data_type = rds.get(key_type)
        data = rds.get(key)
        filename = rds.get(key_filename)
        if data and data_type:
            data = b64encode(data).decode()
            data_type = data_type.decode()
            filename = filename.decode() if filename else None
            rds.decr(key_view_count)
            if parsed_integer <= 1:
                rds.delete(key)
                rds.delete(key_type)
                rds.delete(key_view_count)
                rds.delete(key_filename)
            return render_template("view.html", b64_data=data, data_type=data_type, filename=filename), 200
   
    abort(404)


if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT)