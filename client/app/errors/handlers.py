from werkzeug.exceptions import HTTPException
from app.errors import bp
import json

@bp.app_errorhandler(HTTPException)
def handle_exception(error):
    response = error.get_response()
    response.data = json.dumps({
        "code": error.code,
        "name": error.name,
        "description": error.description,
    }, indent=2)
    response.content_type = "application/json"
    return response