from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from config import settings
import json, secrets

# with open("app/data/credentials/account-pass.jsonld", "r") as f:
#     credential_example = json.loads(f.read())
#     # credential_example["issuer"] = settings.AGENT_WALLETS[0]["did"]
#     # credential_example["issuer"] = settings.DID_WEB
#     credential_example["issuanceDate"] = (
#         str(datetime.now()).split(".")[0].replace(" ", "T") + "Z"
#     )

with open("app/data/templates/verifiable_credential.jsonld", "r") as f:
    verifiable_credential_example = json.loads(f.read())

with open("app/data/presentation_requests/account-pass.json", "r") as f:
    presentation_request_example = json.loads(f.read())


with open("app/data/credentials/food-safety.jsonld", "r") as f:
    credential_example = json.loads(f.read())
    credential_example["issuanceDate"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    credential_example["issuer"]["id"] = f"did:sov:{settings.AGENT_DID}"

class DefinitionInput(BaseModel):
    credential: dict = credential_example
    options: dict = {
        "revocation": False
    }


class IssueCredentialInput(BaseModel):
    credential: dict = Field(example=credential_example)
    options: Optional[dict] = Field(default={}, example={})


class VerifyCredentialInput(BaseModel):
    verifiable_credential: dict = Field(example=verifiable_credential_example)
    options: Optional[dict] = Field(default={}, example={})


class HandshakeInput(BaseModel):
    alias: Optional[str] = Field(default=None)


class CredentialOfferInput(BaseModel):
    credential: dict = {
        "@context": [
        "https://www.w3.org/2018/credentials/v1",
        "https://contexts.vcplayground.org/examples/food-safety-certification/v1.json",
        "https://w3id.org/security/suites/ed25519-2020/v1",
        "https://andrewwhitehead.github.io/anoncreds-w3c-mapping/schema.json",
        {
            "@vocab": "urn:anoncreds:attributes#"
        }
        ],
        "credentialSubject": {
        "certification.certificateId": "urn:uuid:8460c404-c0a5-4653-aeae-44d03a1a7334",
        "certification.examDate": "20111111",
        "certification.testCode": "urn:uuid:df52b514-e13a-42b7-8030-3f928a27d167",
        "certification.type": "FoodSafetyCertification",
        "name": "Jane Doe"
        },
        "description": "This individual has passed the SafeChef Food Safety Certification examination successfully.",
        "issuanceDate": "2023-10-18T14:22:58Z",
        "issuer": {
        "id": "did:sov:RzWHypcqRZSB1prwXnApsS",
        "name": "Food Safety Certifiers, Inc."
        },
        "type": [
        "FoodSafetyCertificationCredential",
        "VerifiableCredential",
        "AnonCredsCredential"
        ],
        "credentialSchema": {
        "type": "AnonCredsSchema2022",
        "id": "RzWHypcqRZSB1prwXnApsS:2:FoodSafetyCertificationCredential:0.1",
        "definition": "RzWHypcqRZSB1prwXnApsS:3:CL:85223:Food Safety Certification Credential"
        }
    }
    # schema_id: str = settings.DEMO_SCHEMA_ID
    # attributes: dict = {
    #     "display_name": "Demo User",
    #     "email": "user@idlab.org",
    #     "organization": "IDLab",
    #     "role": "owner",
    # }
    # credential: dict = credential_example


class PresentProofInput(BaseModel):
    restriction_id: str = settings.DEMO_CRED_DEF_ID
    attributes: list = ["name", "certification.certificateId"]
    predicates: list = [("certification.examDate", "<=20230607")]
    # presentation_request: dict = presentation_request_example
    # handshake: Optional[bool] = Field(default=False, example=False)


class OOBInput(BaseModel):
    handshake: dict | None = Field(
        default=None, example={"type": "connections", "alias": "changeme"}
    )
    attachement: dict | None = Field(
        default=None, example={"type": "credential-offer", "filter": "indy"}
    )
