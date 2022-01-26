from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

def permission_required(permission):
    """Function decorator used so that only those
    who have been confirmed can access

    Args:
        permission (int): The permission given based on the list in Permission class from app.models
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Function decorator used so that only admins can access
    """
    return permission_required(Permission.ADMIN)(f)