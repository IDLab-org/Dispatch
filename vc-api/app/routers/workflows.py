from fastapi import APIRouter, HTTPException
from starlette.responses import StreamingResponse
from config import settings
from app.models import CredentialOfferInput, PresentProofInput
from app.controllers import agent
import json
from app import functions
from datetime import datetime

router = APIRouter()


@router.post(
    "/credential-offer",
    tags=["Workflows"],
    summary="DIDComm Out-of-Band Credential Offer Attachement",
)
async def credential_offer(
    credential_offer_input: CredentialOfferInput,
    anoncreds: bool = None,
    handshake: bool = None,
    qrcode: bool = None
):
    credential = vars(credential_offer_input)["credential"]
    filter = "indy" if anoncreds else "ld_proof"
    credential_offer = agent.create_credential_offer(
        filer=filter, credential=credential
    )
    cred_ex_id = credential_offer["cred_ex_id"]
    oob_payload = {
        "goal": "To issue a vc",
        "goal_code": "issue-vc",
        "attachement": [{"id": cred_ex_id, "type": "credential-offer"}],
    }
    oob_payload["alias"] = cred_ex_id
    if handshake:
        oob_payload["handshake"] = ["https://didcomm.org/connections/1.0", "https://didcomm.org/didexchange/1.0"]
    oob_invitation = agent.create_oob_invitation(oob_payload)
    with open(f"app/data/oob-invitations/{cred_ex_id}.json", "w") as f:
        f.write(json.dumps(oob_invitation, indent=4))
    data = f"{settings.VC_API_ENDPOINT}/workflows/credential-offer/exchanges/{cred_ex_id}"
    if qrcode:
        buf = functions.generate_qrcode_response(data)
        return StreamingResponse(
            buf, media_type="image/jpeg", headers={"Exchange-Id": cred_ex_id}
        )
    return {"exchange-url": data}

@router.get(
    "/credential-offer/exchanges/{exchange_id}",
    tags=["Workflows"],
    # summary="Recieve a DIDComm Out-of-Band Invitation",
)
async def get_exchange(exchange_id):
    # if workflow_id not in ["connection", "credential-offer", "presentation-request"]:
    #     raise HTTPException(status_code=400)
    try:
        with open(f"app/data/oob-invitations/{exchange_id}.json", "r") as f:
            invitation = json.loads(f.read())
    except:
        raise HTTPException(status_code=400)
    return invitation

@router.post(
    "/presentation-request",
    tags=["Workflows"],
    summary="DIDComm Out-of-Band Present Proof Attachement",
)
async def presentation_request(
    presentation_request_input: PresentProofInput,
    anoncreds: bool = None,
    handshake: bool = None,
    qrcode: bool = None
):
    restriction_id = vars(presentation_request_input)["restriction_id"]
    requested_attributes = vars(presentation_request_input)["attributes"]
    filter = "indy" if anoncreds else "ld_proof"
    restriction = (
        {"schema_id": restriction_id}
        if restriction_id.split(":")[-3] == "2"
        else {"cred_def_id": restriction_id}
    )
    predicates = vars(presentation_request_input)["predicates"]
    presentation_request = {
        "name": "Proof request",
        "version": "1.0",
        "requested_attributes": {
            "attrib_0": {
                "names": requested_attributes,
                "restrictions": [restriction],
            }
        },
        "requested_predicates": {},
    }
    if len(predicates) > 1:
        presentation_request["requested_predicates"] = {
            "predic_0": {
                "name": predicates[0][0],
                "p_type": predicates[0][1][:-8],
                "p_value": int(predicates[0][1][-8:]),
                "restrictions": [restriction],
            }
        }
    # print(json.dumps(presentation_request))
    presentation_request = agent.create_presentation_request(
        filter=filter, presentation_request=presentation_request
    )
    pres_ex_id = presentation_request["pres_ex_id"]
    pres_request = presentation_request["pres_request"]
    pres_request["id"] = pres_ex_id
    pres_request["type"] = "present-proof"

    oob_payload = {
        "goal": "To request a connectionless proof request",
        "goal_code": "connectionless-proof",
        "attachement": [pres_request],
    }
    if handshake:
        oob_payload["handshake"] = ["https://didcomm.org/connections/1.0", "https://didcomm.org/didexchange/1.0"]
    oob_invitation = agent.create_oob_invitation(oob_payload)
    with open(f"app/data/oob-invitations/{pres_ex_id}.json", "w") as f:
        f.write(json.dumps(oob_invitation, indent=4))
    data = f"{settings.VC_API_ENDPOINT}/workflows/presentation-request/exchanges/{pres_ex_id}"
    if qrcode:
        buf = functions.generate_qrcode_response(data)
        return StreamingResponse(
            buf, media_type="image/jpeg", headers={"Exchange-Id": pres_ex_id}
        )
    return {"exchange-url": data}


# @router.delete(
#     "",
#     tags=["Workflows"],
#     summary="Delete all exchanges",
#     status_code=200,
#     # include_in_schema=False,
# )
# async def delete_exchanges():
#     agent.delete_cred_exchanges()
#     agent.delete_pres_exchanges()

#     return ""


@router.get(
    "/presentation-request/exchanges/{exchange_id}",
    tags=["Workflows"],
    # summary="Recieve a DIDComm Out-of-Band Invitation",
)
async def get_exchange(exchange_id):
    # if workflow_id not in ["connection", "credential-offer", "presentation-request"]:
    #     raise HTTPException(status_code=400)
    try:
        with open(f"app/data/oob-invitations/{exchange_id}.json", "r") as f:
            invitation = json.loads(f.read())
    except:
        raise HTTPException(status_code=400)
    return invitation


# @router.get(
#     "/exchanges/{exchange_id}/connection",
#     tags=["Workflows"],
#     # summary="Recieve a DIDComm Out-of-Band Invitation",
# )
# async def get_connection(exchange_id):
#     connection = agent.get_connection_state(exchange_id)

#     return connection
