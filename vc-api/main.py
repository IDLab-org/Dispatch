from fastapi import FastAPI, APIRouter, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse
from starlette.requests import Request
from starlette.responses import RedirectResponse
from app.routers import credentials, exchanges, presentations, workflows
from app.controllers import agent
from config import settings
import json

# agent.cache_did_document()

# multi_use_invitation = agent.create_multi_use_invitation()
# with open(f"app/data/oob-invitations/multi.json", "w") as f:
#     f.write(json.dumps(multi_use_invitation["invitation"], indent=4))

app = FastAPI(
    title=settings.PROJECT_TITLE,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
    contact=settings.PROJECT_CONTACT,
    license_info=settings.PROJECT_LICENSE_INFO,
)


@app.exception_handler(RequestValidationError)
async def handler(request: Request, exc: Exception):
    response = Response()
    response.status_code = 400
    return Response(status_code=400)


api_router = APIRouter()


@api_router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index():
    return RedirectResponse(url="/docs")


@api_router.get("/logo", include_in_schema=False)
async def get_logo():
    return FileResponse("app/data/images/logo.png")


@api_router.get("/.well-known/did.json", include_in_schema=False)
async def well_known_did():
    with open("app/data/did_document.json", "r") as f:
        did_doc = json.loads(f.read())
    return did_doc

api_router.include_router(credentials.router, prefix="/credentials")
# api_router.include_router(presentations.router, prefix="/presentations")
# api_router.include_router(exchanges.router, prefix="/exchanges")
api_router.include_router(workflows.router, prefix="/workflows")

app.include_router(api_router)
