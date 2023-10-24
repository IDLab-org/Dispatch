from flask import current_app, render_template, url_for, redirect, session, request, flash
from app.routes.main import bp
from .forms import OOBForm
import json, requests

@bp.route("/", methods=["GET", "POST"])
def index():
    form = OOBForm()
    form.attachement.choices = [
        ("credential_offer", "Offer"),
        ("proof_request", "Request")
    ]
    invitation = None
    didcomm_url = None
    invitation_url = None
    if request.method == "POST" and form.is_submitted():
        handshake = form.handshake.data
        if form.attachement.data == "credential_offer":
            payload = {
                "credentialSubject": {
                    "email": "demo.user@idlab.org",
                    "join_date": "20231024",
                    "full_name": "Demo User",
                    "organization": "IDLab"
                },
                "credentialSchema": {
                    "id": "VA56jZQD1V8dvhzD6vBqP4:2:PlatformUserCredential:1.0",
                    "definition": "VA56jZQD1V8dvhzD6vBqP4:3:CL:103060:DTT Platform User Credential"
                }
            }
            r = requests.post(f"https://vc-api.dtt.idlab.app/workflows/credential-offer?anoncreds=True&handshake={handshake}", json=payload)
        if form.attachement.data == "proof_request":
            payload = {
                "restriction_id": "VA56jZQD1V8dvhzD6vBqP4:3:CL:103060:DTT Platform User Credential",
                "attributes": [
                    "email",
                    "organization"
                ],
                "predicates": [
                    [
                    "join_date",
                    ">=20230607"
                    ]
                ]
            }
            r = requests.post(f"https://vc-api.dtt.idlab.app/workflows/presentation-request?anoncreds=True&handshake={handshake}", json=payload)
        invitation_url = r.json()["exchange-url"]
        didcomm_url = invitation_url.replace("https://", "didcomm://")
        r = requests.get(invitation_url)
        invitation = json.dumps(r.json(), indent=2)

    return render_template(
        "pages/index.jinja",
        form=form,
        didcomm_url=didcomm_url,
        invitation_url=invitation_url,
        invitation=invitation
        )
