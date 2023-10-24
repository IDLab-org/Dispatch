from fastapi import APIRouter, HTTPException
from config import settings
from app.models import IssueCredentialInput, DefinitionInput, CredentialOfferInput
from app.controllers import agent
from app import functions
import flatdict

router = APIRouter()


@router.post("/define", tags=["Credentials"], summary="Publish a credential definition", status_code=201)
async def define_credential(definition_input: DefinitionInput):
    options = vars(definition_input)["options"]
    if options["revocation"]:
        raise HTTPException(status_code=400)
    credential = vars(definition_input)["credential"]
    credential["type"].remove("VerifiableCredential")
    credential["credentialSubject"] = dict(flatdict.FlatDict(credential["credentialSubject"], delimiter='.'))
    schema = {
        "schema_name": credential["type"][0],
        "schema_version": "0.1",
        "attributes": [attribute for attribute in credential["credentialSubject"]]
    }
    schema_id = agent.create_schema(schema)
    cred_def = {
        # "revocation_registry_size": 1000,
        "schema_id": schema_id,
        "support_revocation": False,
        "tag": ''.join(' ' + char if char.isupper() else char.strip() for char in schema_id.split(":")[-2]).strip(),
    }
    
    cred_def_id = agent.get_cred_def(schema_id, cred_def)

    credential = vars(definition_input)["credential"]
    credential["@context"].append("https://andrewwhitehead.github.io/anoncreds-w3c-mapping/schema.json")
    credential["@context"].append({"@vocab": "urn:anoncreds:attributes#"})
    credential["type"].append("VerifiableCredential")
    credential["type"].append("AnonCredsCredential")
    credential["credentialSubject"] = dict(flatdict.FlatDict(credential["credentialSubject"], delimiter='.'))
    credential["credentialSchema"] = {
        "type": "AnonCredsSchema2022",
        "id": schema_id,
        "definition": cred_def_id,
    }
    # credential["proof"] = {
    #     "type": "CLSignature2022"
    # }
    return {"credential": credential}

# @router.post(
#     "/offer",
#     tags=["Credentials"],
#     summary="Attach a credential offer to an OOB invitation",
# )
# async def credential_offer(
#     credential_offer_input: CredentialOfferInput,
#     handshake: bool = None,
#     filter: str = "indy",
#     qrcode: bool = None,
#     connection_id: str = None,
# ):
#     if filter not in ["indy", "ld_proof"]:
#         raise HTTPException(status_code=400)
#     # credential = vars(credential_offer_input)["credential"]
#     if filter == "indy":
#         schema_id = vars(credential_offer_input)["schema_id"]
#         attributes = vars(credential_offer_input)["attributes"]
#         cred_def = {
#             # "revocation_registry_size": 1000,
#             "schema_id": schema_id,
#             "support_revocation": False,
#             "tag": schema_id.split(":")[-2].capitalize(),
#         }
#         cred_def_id = agent.get_cred_def(schema_id, cred_def)
#         credential = {
#             "@context": [
#                 "https://www.w3.org/ns/credentials/v2",
#                 "https://www.hyperledger.org/ns/anoncreds/v1",
#                 {"@vocab": "urn:anoncreds:attributes#"},
#             ],
#             "issuer": settings.AGENT_DID,
#             "type": ["VerifiableCredential", "AnonCredsCredential"],
#             "validityDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
#             "credentialSchema": {
#                 "type": "AnoncredsSchema2022",
#                 "id": schema_id,
#                 "def": cred_def_id,
#             },
#             "credentialStatus": {
#                 "type": "AnonCredsRevocation2022",
#                 "id": "rev_registry_definition_id",  # REVOC_REG_DEF {did}:4:{cred_def_id}:CL_ACCUM:{cl_accum}
#                 "tails": "https://tails.dtt.idlab.app#hash",
#                 "cred": "cred_rev_id",
#             },
#             "credentialSubject": attributes,
#             "proof": {"type": "CLSignature2022"},
#         }
#         if not cred_def_id:
#             raise HTTPException(status_code=400)
#         if connection_id:
#             try:
#                 agent.issue_credential(credential, connection_id)
#                 return ""
#             except:
#                 raise HTTPException(status_code=400)
#     elif filter == "ld_proof":
#         credential = vars(credential_offer_input)["credential"]

#     credential_offer = agent.create_credential_offer(
#         filer=filter, credential=credential
#     )
#     cred_ex_id = credential_offer["cred_ex_id"]
#     oob_payload = {
#         "goal": "To issue a vc",
#         "goal_code": "issue-vc",
#         "attachement": [{"id": cred_ex_id, "type": "credential-offer"}],
#     }
#     if handshake:
#         oob_payload["alias"] = cred_ex_id
#         oob_payload["handshake"] = ["https://didcomm.org/connections/1.0"]
#     oob_invitation = agent.create_oob_invitation(oob_payload)
#     with open(f"app/data/oob-invitations/{oob_invitation['@id']}.json", "w") as f:
#         f.write(json.dumps(oob_invitation, indent=4))
#     data = f"{settings.VC_API_ENDPOINT}/workflows/exchanges/{oob_invitation['@id']}"
#     if qrcode:
#         buf = functions.generate_qrcode_response(data)
#         return StreamingResponse(
#             buf, media_type="image/jpeg", headers={"Exchange-Id": oob_invitation["@id"]}
#         )
#     return {"exchange-url": data}

@router.post("/issue", tags=["Credentials"], summary="Issue VC", status_code=201)
async def issue_credential(issue_credential_input: IssueCredentialInput):
    if not vars(issue_credential_input).get("credential"):
        raise HTTPException(status_code=400)

    credential = vars(issue_credential_input)["credential"]
    options = vars(issue_credential_input)["options"]
    if not functions.validate_credential(credential):
        raise HTTPException(status_code=400)

    verifiable_credential = agent.sign_jsonld(
        credential,
        settings.AGENT_VERKEY,
        f"did:sov:{settings.AGENT_DID}#key-1",
    )
    if not verifiable_credential:
        # MUST successfully issue a credential.
        raise HTTPException(status_code=400)
    return {"verifiableCredential": verifiable_credential}
