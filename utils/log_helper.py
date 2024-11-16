from database import db, ActivityLog


def log_activity(admin_id, action, description=None):
    """
    Log an admin's activity using the updated ActivityLog model.
    """
    try:
        if not description:
            description = f"{action} by admin ID: {admin_id}"

        if not isinstance(admin_id, int):
            raise ValueError("Failed to log activity")

        # Sanitize action input
        if not action or not isinstance(action, str):
            raise ValueError("Failed to log activity")

        action = action[:255]  # Limit to 255 characters
        new_log = ActivityLog(
            admin_id=admin_id,
            action=action,
            description=description
        )
        db.session.add(new_log)
        db.session.commit()
    except Exception as e:
        # Handle logging errors gracefully
        print("Failed to log activity")
