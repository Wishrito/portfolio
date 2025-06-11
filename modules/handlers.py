from pathlib import Path

from flask import render_template

from .classes import Error

handler_bp = Error("errors", __name__)


@handler_bp.app_errorhandler(404)
def page_not_found(error):
    """
    Handle 404 Page Not Found error by rendering a custom error page.

    Args:
        error: The error object containing details about the 404 error.

    Returns:
        A rendered template for the 404 error page.
    """
    return render_template("errors/404.j2", e=error)


@handler_bp.app_errorhandler(403)
def forbidden(error):
    """
    Handle 403 Forbidden errors by rendering a custom error page.

    Args:
        error: The error object containing details about the 403 error.

    Returns:
        A rendered HTML template for the 403 error page.
    """
    return render_template("errors/403.j2", e=error)
