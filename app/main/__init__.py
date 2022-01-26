from flask import Blueprint
from app.models import Permission

main = Blueprint('main', __name__)

@main.app_context_processor
def inject_permissions():
    """Access the Permission database table/class without needing to call it every time
    you need to pass it into functions.
    """
    return dict(Permission=Permission)

from . import views, forms, errors