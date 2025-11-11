"""
Account Service

This microservice handles the lifecycle of Accounts.
"""
from typing import Any
from flask import jsonify, request, make_response, abort, url_for
from service.models import Account
from service.common import status
from . import app


############################################################
# HEALTH ENDPOINT
############################################################
@app.route("/health", methods=["GET"])
def health() -> Any:
    """Health status endpoint"""
    return jsonify(status="OK"), status.HTTP_200_OK


############################################################
# INDEX ENDPOINT
############################################################
@app.route("/", methods=["GET"])
def index() -> Any:
    """Root URL response"""
    return jsonify(
        name="Account REST API Service",
        version="1.0"
    ), status.HTTP_200_OK


############################################################
# CREATE ACCOUNT
############################################################
@app.route("/accounts", methods=["POST"])
def create_account() -> Any:
    """Creates a new Account"""
    app.logger.info("Request to create an Account")
    check_content_type("application/json")

    data = request.get_json()
    account = Account()
    try:
        account.deserialize(data)
        account.create()
    except Exception as e:
        app.logger.error("Failed to create account: %s", e)
        abort(status.HTTP_400_BAD_REQUEST, f"Invalid account data: {e}")

    location_url = url_for("get_account", account_id=account.id, _external=True)
    return make_response(jsonify(account.serialize()),
                         status.HTTP_201_CREATED,
                         {"Location": location_url})


############################################################
# LIST ALL ACCOUNTS
############################################################
@app.route("/accounts", methods=["GET"])
def list_accounts() -> Any:
    """Returns a list of all accounts"""
    app.logger.info("Request to list all Accounts")
    accounts = Account.all()
    return jsonify([acct.serialize() for acct in accounts]), status.HTTP_200_OK


############################################################
# READ ACCOUNT
############################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_account(account_id: int) -> Any:
    """Returns a single Account by ID"""
    app.logger.info("Request to read Account with id: %s", account_id)
    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND,
              f"Account with id [{account_id}] could not be found.")
    return jsonify(account.serialize()), status.HTTP_200_OK


############################################################
# UPDATE ACCOUNT
############################################################
@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id: int) -> Any:
    """Updates an existing Account by ID"""
    app.logger.info("Request to update Account with id: %s", account_id)
    check_content_type("application/json")

    account = Account.find(account_id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND,
              f"Account with id [{account_id}] could not be found.")

    data = request.get_json()
    try:
        account.deserialize(data)
        account.update()
    except Exception as e:
        app.logger.error("Failed to update account: %s", e)
        abort(status.HTTP_400_BAD_REQUEST, f"Invalid account data: {e}")

    return jsonify(account.serialize()), status.HTTP_200_OK


############################################################
# DELETE ACCOUNT
############################################################
@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id: int) -> Any:
    """Deletes an Account by ID"""
    app.logger.info("Request to delete Account with id: %s", account_id)
    account = Account.find(account_id)
    if account:
        account.delete()
    # Return 204 even if the account was not found
    return "", status.HTTP_204_NO_CONTENT


############################################################
# UTILITY FUNCTION
############################################################
def check_content_type(media_type: str) -> None:
    """Validates the Content-Type of the request"""
    content_type = request.headers.get("Content-Type")
    if content_type != media_type:
        app.logger.error("Invalid Content-Type: %s", content_type)
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
              f"Content-Type must be {media_type}")

