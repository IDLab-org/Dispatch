from fastapi import APIRouter, HTTPException
from starlette.responses import StreamingResponse
from config import settings
from app.models import *
from app.controllers import agent
import json, requests
from app import functions

router = APIRouter()


@router.post(
    "/request",
    tags=["Presentations"],
    summary="Attach a presentation request to an OOB invitation",
)
async def presentation_request(
    presentation_request_input: PresentProofInput,
    handshake: bool = None,
    filter: str = "indy",
    qrcode: bool = None,
    # connection_id: str = None,
):
    # presentation_request = vars(presentation_request_input)["presentation_request"]
    restriction_id = vars(presentation_request_input)["restriction_id"]
    requested_attributes = vars(presentation_request_input)["attributes"]
    if filter not in ["indy", "ld_proof"]:
        raise HTTPException(status_code=400)
    restriction = (
        {"schema_id": restriction_id}
        if restriction_id.split(":")[-3] == "2"
        else {"cred_def_id": restriction_id}
    )
    presentation_request = {
        "name": "Proof request",
        "version": "1.0",
        "requested_attributes": {
            "request": {
                "names": requested_attributes,
                "restrictions": [restriction],
            }
        },
        "requested_predicates": {},
    }
    presentation_request = agent.create_presentation_request(
        filter=filter, presentation_request=presentation_request
    )
    pres_ex_id = presentation_request["pres_ex_id"]
    pres_request = presentation_request["pres_request"]
    # pres_req_dict = presentation_request["presentation_request_dict"]
    pres_request["id"] = pres_ex_id
    pres_request["type"] = "present-proof"

    oob_payload = {
        "goal": "To request a connectionless proof request",
        "goal_code": "connectionless-proof",
        "attachement": [pres_request],
    }
    if handshake:
        oob_payload["alias"] = pres_ex_id
        oob_payload["handshake"] = ["https://didcomm.org/connections/1.0"]
    oob_invitation = agent.create_oob_invitation(oob_payload)
    with open(f"app/data/oob-invitations/{oob_invitation['@id']}.json", "w") as f:
        f.write(json.dumps(oob_invitation, indent=4))
    data = f"{settings.VC_API_ENDPOINT}/exchanges/{oob_invitation['@id']}"
    if qrcode:
        buf = functions.generate_qrcode_response(data)
        return StreamingResponse(
            buf, media_type="image/jpeg", headers={"Exchange-Id": oob_invitation["@id"]}
        )
    return {"exchange-url": data}
