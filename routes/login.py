
from flask import send_file, Blueprint
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token



login = Blueprint('login', __name__)



@login.route("/login", methods=["POST"]) 
def login_auth():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if username != "admin" or password != "admin":  
        return jsonify({"msg": "Bad username or password"}), 401

    # Generate token for authenticated user
    access_token = create_access_token(identity={"username": username})
    return jsonify(access_token=access_token)
