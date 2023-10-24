from flask import current_app, render_template, url_for, redirect, session, request, flash, send_file
from app.routes.main import bp
from .models import *
import requests

@bp.before_request
def before_request_callback():
    pass

@bp.route("/", methods=["GET", "POST"])
def index():
    # r = requests.post(current_app.config["VC_API_ENDPOINT"]+"/workflows/connection")
    # session['exchange_http'] = r.json()["exchange-url"]
    # session['exchange_didcomm'] = session['exchange_http'].replace('https://', 'didcomm://')
    # session['exchange_id'] = session['exchange_http'].split("/")[-1]
    # r = requests.get(current_app.config["VC_API_ENDPOINT"]+f"/workflows/exchanges/{session['exchange_id']}/connection")
    # session['connection_id'] = r.json()["connection_id"]
    
    # r = requests.post(current_app.config["VC_API_ENDPOINT"]+"/workflows/proof-request", json=proof_rebate)
    # r = requests.post(current_app.config["VC_API_ENDPOINT"]+"/workflows/proof-request", json=proof_showtime)
    # r = requests.post(current_app.config["VC_API_ENDPOINT"]+"/workflows/proof-request", json=proof_address)
    return render_template("pages/index.jinja")
