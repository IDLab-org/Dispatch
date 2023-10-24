import requests, json
from config import settings


def cache_did_document():
    r = requests.get(
        f"{settings.AGENT_ADMIN_ENDPOINT}/resolver/resolve/{settings.AGENT_WALLETS[0]['did']}"
    )
    did_doc = r.json()["did_document"]
    with open("app/data/did_document.json", "w") as f:
        f.write(json.dumps(did_doc, indent=4))


def create_wallet(method, key_type, seed=None):
    payload = {"method": method, "options": {"key_type": key_type}}
    if seed:
        payload["seed"] = seed
    r = requests.post(
        settings.AGENT_ADMIN_ENDPOINT + "/wallet/did/create",
        headers=settings.AGENT_REQUEST_HEADERS,
        json=payload,
    )
    return r.json()["result"]


def create_schema(schema):
    requests.post(
        settings.AGENT_ADMIN_ENDPOINT + "/schemas",
        headers=settings.AGENT_REQUEST_HEADERS,
        json=schema,
    )
    return f"{settings.AGENT_DID}:2:{schema['schema_name']}:{schema['schema_version']}"


def get_cred_def(schema_id, cred_def):
    r = requests.get(
        settings.AGENT_ADMIN_ENDPOINT
        + f"/credential-definitions/created?schema_id={schema_id}"
    )
    if len(r.json()["credential_definition_ids"]) > 0:
        return r.json()["credential_definition_ids"][0]
    r = requests.post(
        settings.AGENT_ADMIN_ENDPOINT + f"/credential-definitions",
        json=cred_def,
        headers=settings.AGENT_REQUEST_HEADERS,
    )
    if r.status_code != 200:
        return None
    return r.json()["credential_definition_id"]


def get_connection_id(msg_id):
    r = requests.get(
        settings.AGENT_ADMIN_ENDPOINT + f"/connections?invitation_msg_id={msg_id}"
    )
    return r.json()["results"][0]["connection_id"]


def get_connection_state(exchange_id):
    r = requests.get(
        settings.AGENT_ADMIN_ENDPOINT + f"/connections?invitation_msg_id={exchange_id}"
    )
    if len(r.json()["results"]) > 0:
        connection = r.json()["results"][0]
        r = requests.get(
            settings.AGENT_ADMIN_ENDPOINT
            + f"/connections/{connection['connection_id']}/endpoints"
        )
        connection = {
            "state": connection["state"],
            "endpoint": r.json()["their_endpoint"] if r.status_code == 200 else None,
            "connection_id": connection["connection_id"],
        }
        return connection
    return None


def delete_connection(exchange_id):
    r = requests.get(
        settings.AGENT_ADMIN_ENDPOINT + f"/connections?invitation_msg_id={exchange_id}"
    )
    connection = r.json()["results"][0]
    if connection:
        requests.delete(
            settings.AGENT_ADMIN_ENDPOINT
            + f"/connections/{connection['connection_id']}"
        )


def get_connections(alias=None):
    if alias:
        r = requests.get(settings.AGENT_ADMIN_ENDPOINT + f"/connections?alias={alias}")
    else:
        r = requests.get(settings.AGENT_ADMIN_ENDPOINT + "/connections")
    connections = r.json()["results"]
    return connections


def delete_connections():
    r = requests.get(settings.AGENT_ADMIN_ENDPOINT + "/connections")
    for connection in r.json()["results"]:
        if connection.get("alias") and connection["alias"] == "multi":
            pass
        else:
            requests.delete(
                settings.AGENT_ADMIN_ENDPOINT
                + f"/connections/{connection['connection_id']}"
            )


def create_multi_use_invitation():
    invitation = {
        "accept": ["didcomm/aip1", "didcomm/aip2;env=rfc19"],
        "alias": "multi",
        "goal": "connect",
        "goal_code": "connect",
        "metadata": {},
        "my_label": settings.AGENT_LABEL,
        "protocol_version": "1.1",
        "use_public_did": False,
    }
    invitation["handshake_protocols"] = ["https://didcomm.org/connections/1.0"]
    r = requests.post(
        f"{settings.AGENT_ADMIN_ENDPOINT}/out-of-band/create-invitation?multi_use=true",
        headers=settings.AGENT_REQUEST_HEADERS,
        json=invitation,
    )
    if r.status_code != 200:
        return None

    return r.json()


def sign_jsonld(document, verkey, verification_method):
    payload = {
        "doc": {
            "credential": document,
            "options": {
                "proofPurpose": "assertionMethod",
                "verificationMethod": verification_method,
            },
        },
        "verkey": verkey,
    }
    r = requests.post(
        f"{settings.AGENT_ADMIN_ENDPOINT}/jsonld/sign",
        headers=settings.AGENT_REQUEST_HEADERS,
        json=payload,
    )
    if r.status_code != 200 or "signed_doc" not in r.json():
        return False
    return r.json()["signed_doc"]


def verify_jsonld(document, verkey):
    payload = {"doc": document, "verkey": verkey}
    r = requests.post(
        f"{settings.AGENT_ADMIN_ENDPOINT}/jsonld/verify",
        headers=settings.AGENT_REQUEST_HEADERS,
        json=payload,
    )
    if r.status_code != 200:
        print(json.dumps(document, indent=4))
        return False
    return r.json()


def get_credentials():
    r = requests.get(f"{settings.AGENT_ADMIN_ENDPOINT}/credentials")
    credentials = r.json()["results"]
    r = requests.post(
        f"{settings.AGENT_ADMIN_ENDPOINT}/credentials/w3c",
        headers=settings.AGENT_REQUEST_HEADERS,
        json={},
    )
    for credential in r.json()["results"]:
        credentials.append(credential)
    return credentials


def create_credential_offer(filer, credential, comment=None):
    if filer == "ld_proof":
        credential_offer = {
            "credential": credential,
            "options": {
                "proofType": "Ed25519Signature2018",
                "proofPurpose": "assertionMethod"
                },
        }
        attributes = []
    elif filer == "indy":
        schema_id = credential["credentialSchema"]["id"]
        cred_def_id = credential["credentialSchema"]["definition"]
        credential_offer = {
            "cred_def_id": cred_def_id,
            "issuer_did": cred_def_id.split(":")[-5],
            "schema_id": schema_id,
            "schema_issuer_did": schema_id.split(":")[-4],
            "schema_name": schema_id.split(":")[-2],
            "schema_version": schema_id.split(":")[-1],
        }
        attributes = []
        for attribute in credential["credentialSubject"]:
            attributes.append(
                {"name": attribute, "value": credential["credentialSubject"][attribute]}
            )
    body = {
        "auto_remove": False,
        "auto_issue": True,
        "auto_offer": True,
        "comment": comment,
        "credential_preview": {
            "@type": "issue-credential/2.0/credential-preview",
            "attributes": attributes,
        },
        "filter": {filer: credential_offer},
        "trace": True,
    }
    # print(json.dumps(body, indent=4))
    r = requests.post(
        f"{settings.AGENT_ADMIN_ENDPOINT}/issue-credential-2.0/create",
        headers=settings.AGENT_REQUEST_HEADERS,
        json=body,
    )
    print(r.text)
    if r.status_code != 200:
        return None

    return r.json()


def create_presentation_request(filter, presentation_request, comment=None):
    body = {
        "auto_verify": True,
        "comment": comment,
        "presentation_request": {filter: presentation_request},
        "trace": True,
    }
    print(json.dumps(body))
    r = requests.post(
        f"{settings.AGENT_ADMIN_ENDPOINT}/present-proof-2.0/create-request",
        headers=settings.AGENT_REQUEST_HEADERS,
        json=body,
    )

    if r.status_code != 200:
        return None
    return r.json()


def create_oob_invitation(invitation_data):
    invitation = {
        "accept": ["didcomm/aip1", "didcomm/aip2;env=rfc19"],
        # "goal": invitation_data["goal"],
        # "goal_code": invitation_data["goal_code"],
        # "metadata": {},
        # "my_label": settings.AGENT_LABEL,
        # "protocol_version": "1.1",
        # "use_public_did": False,
    }
    if invitation_data.get("alias"):
        invitation["alias"] = invitation_data["alias"]
    if invitation_data.get("handshake"):
        invitation["handshake_protocols"] = invitation_data["handshake"]
    if invitation_data.get("attachement"):
        invitation["attachments"] = invitation_data["attachement"]
    print(json.dumps(invitation))
    r = requests.post(
        f"{settings.AGENT_ADMIN_ENDPOINT}/out-of-band/create-invitation",
        headers=settings.AGENT_REQUEST_HEADERS,
        json=invitation,
    )
    if r.status_code != 200:
        return None
    return r.json()["invitation"]


def issue_credential(credential, connection_id):
    schema_id = credential["credentialSchema"]["id"]
    cred_def_id = credential["credentialSchema"]["def"]
    indy_credential = {
        "cred_def_id": cred_def_id,
        "issuer_did": cred_def_id.split(":")[-5],
        "schema_id": schema_id,
        "schema_issuer_did": schema_id.split(":")[-4],
        "schema_name": schema_id.split(":")[-2],
        "schema_version": schema_id.split(":")[-1],
    }
    # w3c_credential = {
    #     "credential": credential,
    #     "options": {"proofType": "Ed25519Signature2018"},
    # }
    attributes = []
    for attribute in credential["credentialSubject"]:
        attributes.append(
            {"name": attribute, "value": credential["credentialSubject"][attribute]}
        )
    payload = {
        "auto_remove": False,
        "comment": "DTT Test Credential",
        "connection_id": connection_id,
        "credential_preview": {
            "@type": "issue-credential/2.0/credential-preview",
            "attributes": attributes,
        },
        "filter": {
            "indy": indy_credential,
            # "ld_proof": w3c_credential
        },
        "trace": True,
        # "verification_method": "string"
    }
    r = requests.post(
        f"{settings.AGENT_ADMIN_ENDPOINT}/issue-credential-2.0/send",
        headers=settings.AGENT_REQUEST_HEADERS,
        json=payload,
    )


def delete_cred_exchanges():
    r = requests.get(f"{settings.AGENT_ADMIN_ENDPOINT}/issue-credential-2.0/records")
    exchanges = r.json()["results"]
    for exchange in exchanges:
        exchange_id = exchange["cred_ex_record"]["cred_ex_id"]
        requests.delete(
            f"{settings.AGENT_ADMIN_ENDPOINT}/issue-credential-2.0/records/{exchange_id}"
        )


def delete_pres_exchanges():
    r = requests.get(f"{settings.AGENT_ADMIN_ENDPOINT}/present-proof-2.0/records")
    exchanges = r.json()["results"]
    for exchange in exchanges:
        exchange_id = exchange["pres_ex_id"]
        requests.delete(
            f"{settings.AGENT_ADMIN_ENDPOINT}/present-proof-2.0/records/{exchange_id}"
        )
