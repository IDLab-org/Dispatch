from fastapi import APIRouter, HTTPException
from config import settings
from app.controllers import agent

router = APIRouter()


# @router.get("", tags=["Connections"], summary="Get Connections", status_code=200)
# async def get_connections(alias: str | None = None):
#     connections = agent.get_connections(alias)

#     return connections


# @router.delete("", tags=["Connections"], summary="Delete Connections", status_code=200)
# async def delete_connections():
#     agent.delete_connections()


@router.get(
    "/{exchange_id}",
    tags=["Connections"],
    summary="Get Connection associated with an exchange id",
    status_code=200,
)
async def get_connection(exchange_id):
    connection = agent.get_connection_state(exchange_id)

    return connection


@router.delete(
    "/{exchange_id}",
    tags=["Connections"],
    summary="Delete Connection associated with an exchange id",
    status_code=200,
    include_in_schema=False,
)
async def delete_connection(exchange_id):
    agent.delete_connection(exchange_id)

    return ""
