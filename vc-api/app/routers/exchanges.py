from fastapi import APIRouter, HTTPException
from starlette.responses import StreamingResponse
from config import settings
from app.models import CredentialOfferInput, PresentProofInput
from app.controllers import agent
import json
from app import functions
from datetime import datetime

router = APIRouter()

# @router.delete(
#     "",
#     tags=["Exchanges"],
#     summary="Delete all exchanges",
#     status_code=200,
#     include_in_schema=False,
# )
# async def delete_exchanges():
#     agent.delete_cred_exchanges()
#     agent.delete_pres_exchanges()

#     return ""


@router.get(
    "/{exchange_id}",
    tags=["Exchanges"],
    # summary="Recieve a DIDComm Out-of-Band Invitation",
)
async def get_exchange(exchange_id):
    try:
        with open(f"app/data/oob-invitations/{exchange_id}.json", "r") as f:
            invitation = json.loads(f.read())
    except:
        raise HTTPException(status_code=400)
    return invitation


@router.get(
    "/{exchange_id}/connection",
    tags=["Exchanges"],
    summary="Fetch connection associated with an exchange",
)
async def get_connection(exchange_id):
    connection = agent.get_connection_state(exchange_id)

    return connection
