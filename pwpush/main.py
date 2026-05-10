from flask import Flask, abort, request, redirect, render_template, jsonify, url_for, session
from redis import Redis
from os import getenv

from helpers import Secret, random_string, hash_password

APP_HOST = getenv("APP_HOST") or "0.0.0.0"
APP_PORT = getenv("APP_PORT") or "8080"
APP_SECRET_KEY = getenv("APP_SECRET_KEY").encode() if getenv("APP_SECRET_KEY") else random_string(lenght=32).encode()
APP_MAX_DATA_LENGHT = int(getenv("APP_DATA_LENGHT")) if getenv("APP_DATA_LENGHT") else 1024 * 1024
REDIS_HOST = getenv("REDIS_HOST") or "localhost"

rds = Redis(host=REDIS_HOST)
app = Flask(__name__, static_url_path="/static")
app.secret_key = APP_SECRET_KEY


@app.route("/")
def index():
    return render_template("save.html"), 200

@app.route("/create-secret", methods=["POST"])
def create_secret():
    secret = Secret()
    secret_json = request.get_json()

    if secret.set_secret(rds, secret_json, APP_MAX_DATA_LENGHT):
        return jsonify({"status": "ok", "key": secret.key}), 200

    return jsonify({"status": "error"}), 400

@app.route("/secret/<key>", methods=["GET", "POST"])
def redirect_logic(key):
    secret = Secret(key)
    secret_exists, secret_password = secret.secret_exists(rds)

    if secret_exists:
        if request.method == "GET":
            if secret_password:
                session["password_requested"] = True
                return render_template("password.html"), 200
            else:
                session["view_allowed"] = True
                session["key"] = key
                return redirect(url_for("view_secret", key=key))
        elif request.method == "POST" and "password_requested" in session and secret_password:
            password_json = request.get_json()
            if password_json.get("password"):
                user_password = password_json["password"]
                if isinstance(user_password, str) and hash_password(user_password) == secret_password:
                    session["view_allowed"] = True
                    session["key"] = key
                    return jsonify({"status": "ok"}), 200
            
            return jsonify({"status": "error"}), 400
   
    abort(404)

@app.route("/secret/<key>/view", methods=["GET"])
def view_secret(key):
    if "view_allowed" in session and "key" in session and key == session["key"]:
        secret = Secret(key)
        secret_data = secret.get_secret(rds)
        if secret_data and secret_data.get("data"):
            return render_template("view.html", b64_data=secret_data["data"], data_type=secret_data["key_type"], view_count=secret_data["view_count"]-1, filename=secret_data["filename"]), 200
    
    abort(404)

if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT)