from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from database import ActivityLog
from routes.login import role_required

logger = Blueprint('logger', __name__)

@logger.route("/view_logs", methods=["GET"])
@jwt_required()
@role_required("Admin")
def view_logs():
    """
    Fetch and display all activity logs.
    Sorted by the most recent first.
    """
    try:
        # Fetch all logs, sorted by timestamp (most recent first)
        logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).all()

        # Format logs for the response
        result = [
            {
                "log_id": log.log_id,
                "admin_id": log.admin_id,
                "action": log.action,
                "description": log.description,
                "timestamp": log.timestamp
            }
            for log in logs
        ]

        return jsonify({"logs": result}), 200
    except Exception as e:
        # Handle errors gracefully
        return jsonify({"error": f"Failed to fetch logs: {str(e)}"}), 500
