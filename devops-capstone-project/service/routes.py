from flask import Flask, jsonify
from service.models import Account

app = Flask(__name__)

BASE_URL = "/accounts"

@app.route(BASE_URL, methods=["GET"])
def list_accounts():
    accounts = Account.all()
    return jsonify([acc.serialize() for acc in accounts]), 200
