from flask import render_template
from app import db
from . import main

# All three functions return error.html template, but throw different error messages
# based on the error_msg variable

@main.app_errorhandler(403)
def forbidden(e):
    """If site returns 403 error, the forbidden function is called and rendered to the site.

    Returns:
        error_msg: You shouldn't be here.
    """
    error_title = 'Forbidden'
    error_msg = 'You shouldn\'t be here.'
    return render_template('error.html', error_title=error_title, error_msg=error_msg), 403

@main.app_errorhandler(404)
def page_not_found(e):
    """If site returns 404 error, this function will be called to the page.

    Returns:
        error_msg: That page doesn't exist.
    """
    error_title="Page Not Found"
    error_msg="That page doesn't exist."
    return render_template(
        'error.html',
        error_title=error_title,
        error_msg=error_msg), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    """If site returns 500 error, this function will be called to the page.

    Returns:
        error_msg: Sorry, we seem to be experiencing some technical difficulties
    """
    error_title = "Internal Server Error"
    error_msg = "Sorry, we seem to be experiencing some technical difficulties"
    return render_template('error.html',
                           error_title=error_title,
                           error_msg=error_msg), 500