from functools import wraps
from flask import send_file, Blueprint, current_app, jsonify, request, make_response

from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, set_access_cookies, get_csrf_token
from database import Admin

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from extensions import limiter
from datetime import datetime, timedelta
from database import db


ph = PasswordHasher(
    time_cost=2,          # Number of iterations
    memory_cost=19456,    # Memory in KiB (19 MiB)
    parallelism=1         # Number of parallel threads) # Initialize the PasswordHasher
)
login = Blueprint('login', __name__)


# Define the maximum allowed failed attempts and lock duration
MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION = timedelta(minutes=15)


@login.route("/login", methods=["POST"])
@limiter.limit("10 per minute")  # Allow 10 requests per minute per IP
def login_auth():
    name = request.json.get("name", None)
    password = request.json.get("password", None)

    user = Admin.query.filter_by(name=name).first()
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401

    # Check if the account is locked
    if (user.failed_login_attempts or 0) >= MAX_FAILED_ATTEMPTS:
        if datetime.now() < user.locked_until:
            return jsonify({"msg": "Account locked. Try again later."}), 403
        else:
            # Reset the failed attempts and lock status after lock duration expires
            user.failed_login_attempts = 0
            user.locked_until = None
            db.session.commit()

    try:
        # Verify the provided password with the stored hashed password
        ph.verify(user.password, password)
    except VerifyMismatchError:
        # Increment failed attempts
        if user.failed_login_attempts is None:
            user.failed_login_attempts = 0  # Set it to 0 if it is None

        user.failed_login_attempts += 1
        db.session.commit()  # Commit after incrementing failed attempts

        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            # Lock the account
            user.locked_until = datetime.now() + LOCK_DURATION
            db.session.commit()  # Commit the lock status change
            return jsonify({"msg": "Too many failed attempts. Account locked for 15 minutes."}), 403

        return jsonify({"msg": "Bad username or password"}), 401

    # Successful login
    user.failed_login_attempts = 0  # Reset failed attempts on successful login
    user.locked_until = None  # Clear lock status
    db.session.commit()  # Commit changes

    access_token = create_access_token(identity={"id": user.admin_id, "role": user.role})

    # Store the token in an HTTP-only, secure cookie
    response = jsonify({"msg": "Login successful", "csrf_token": get_csrf_token(access_token)})
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

