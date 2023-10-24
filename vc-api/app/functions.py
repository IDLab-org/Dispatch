from starlette.responses import StreamingResponse
import io, qrcode


def validate_credential(credential):
    if (
        credential
        # credential MUST have property "type"
        and credential.get("type")
        # credential MUST have property "issuer"
        and credential.get("issuer")
        # credential MUST have property "@context"
        and credential.get("@context")
        # credential MUST have property "credentialSubject"
        and credential.get("credentialSubject")
        # "credential.type" MUST be an array.
        and isinstance(credential["type"], list)
        # credential "@context" MUST be an array.
        and isinstance(credential["@context"], list)
        # "credential.credentialSubject" MUST be an object
        and isinstance(credential["credentialSubject"], dict)
        # "credential.type" items MUST be strings
        and all(isinstance(item, str) for item in credential["type"])
        # credential "@context" items MUST be strings.
        and all(isinstance(item, str) for item in credential["@context"])
        # "credential.issuer" MUST be a string or an object
        and (
            isinstance(credential["issuer"], str)
            or isinstance(credential["issuer"], dict)
        )
    ):
        return True
    else:
        return False


def generate_qrcode_response(data):
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return buf
