"""
Module: error_handlers

Handles all custom and HTTP errors for the Account Service.
"""
from flask import jsonify
from service.models import DataValidationError
from service import app
from . import status


def make_error_response(status_code: int, error: str, message: str):
    """Utility to create a standardized JSON error response"""
    return jsonify(status=status_code, error=error, message=message), status_code


######################################################################
# CUSTOM EXCEPTIONS
######################################################################
@app.errorhandler(DataValidationError)
def handle_data_validation_error(error):
    """Handles DataValidationError and maps it to HTTP 400"""
    return handle_bad_request(error)


######################################################################
# HTTP ERROR HANDLERS
######################################################################
@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def handle_bad_request(error):
    """400 Bad Request"""
    app.logger.warning(str(error))
    return make_error_response(status.HTTP_400_BAD_REQUEST, "Bad Request", str(error))


@app.errorhandler(status.HTTP_404_NOT_FOUND)
def handle_not_found(error):
    """404 Not Found"""
    app.logger.warning(str(error))
    return make_error_response(status.HTTP_404_NOT_FOUND, "Not Found", str(error))


@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def handle_method_not_allowed(error):
    """405 Method Not Allowed"""
    app.logger.warning(str(error))
    return make_error_response(status.HTTP_405_METHOD_NOT_ALLOWED, "Method Not Allowed", str(error))


@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def handle_unsupported_media_type(error):
    """415 Unsupported Media Type"""
    app.logger.warning(str(error))
    return make_error_response(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported Media Type", str(error))


@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def handle_internal_server_error(error):
    """500 Internal Server Error"""
    app.logger.error(str(error))
    return make_error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error", str(error))
