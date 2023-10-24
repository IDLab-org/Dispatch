from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Settings(BaseSettings):
    PROJECT_TITLE: str = "IDLab vc-api implementation"
    PROJECT_VERSION: str = "v0"
    PROJECT_DESCRIPTION: str = """
    VC-API implementation for the Digital Trust Test Bench from the Digital Identity Laboratory of Canada.
    """
    PROJECT_CONTACT: dict = {
        "name": "IDLab",
        "url": "https://github.com/IDLab-org/Dispatch",
    }
    PROJECT_LICENSE_INFO: dict = {
        "name": "Apache License",
        "url": "http://www.apache.org/licenses/",
    }
    DEMO_SCHEMA_ID: str = "RzWHypcqRZSB1prwXnApsS:2:FoodSafetyCertificationCredential:0.1"
    DEMO_CRED_DEF_ID: str = "RzWHypcqRZSB1prwXnApsS:3:CL:85223:Food Safety Certification Credential"
    VC_API_ENDPOINT: str = os.environ["VC_API_ENDPOINT"]
    DID_WEB: str = f"did:web:{VC_API_ENDPOINT.replace('https://', '')}"
    AGENT_LABEL: str = os.environ["AGENT_LABEL"]
    AGENT_ADMIN_ENDPOINT: str = os.environ["AGENT_ADMIN_ENDPOINT"]
    AGENT_DID: str = os.environ["AGENT_DID"]
    AGENT_VERKEY: str = os.environ["AGENT_VERKEY"]
    AGENT_VERIFICATION_METHOD: str = "did:sov:RzWHypcqRZSB1prwXnApsS#key-1"
    AGENT_WALLETS: list = [
        {
            "key_type": "ed25519",
            "method": "sov",
            "seed": "wC5BEEponuAWXb8ytrcxRjHa9xe7uvLU",
            "did": "did:sov:RzWHypcqRZSB1prwXnApsS",
            "verkey": "Ed2iJTN22vfXjiJjwGrDu8ZGrPinXsprfUG7kk34LSq2",
        }
    ]
    AGENT_REQUEST_HEADERS: dict = {
        "Content-Type": "application/json",
        "accept": "application/json",
    }


settings = Settings()
