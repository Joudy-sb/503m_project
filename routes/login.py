from functools import wraps
from flask import send_file, Blueprint, current_app, jsonify, request, make_response

from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, set_access_cookies
from database import Admin
import jwt

login = Blueprint('login', __name__)


@login.route("/login", methods=["POST"])
def login_auth():
    name = request.json.get("name", None)
    password = request.json.get("password", None)


    user = Admin.query.filter_by(name=name).first()
    if not user or user.password != password:  
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity={"id": user.admin_id, "role": user.role})

    # Store the token in an HTTP-only, secure cookie
    response = make_response({"msg": "Login successful"})
    set_access_cookies(response, access_token)
    return response 

def role_required(allowed_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()  
            user_role = identity.get("role")
            if user_role not in allowed_roles:
                return jsonify({"error": "Permission denied: Insufficient role"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

