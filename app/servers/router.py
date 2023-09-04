from fastapi import APIRouter, Depends, HTTPException
from openstack import connection

from app.dependencies import get_openstack_connection

router = APIRouter(
    prefix="/servers",
    tags=["servers"]
)


@router.get("/list")
async def get_servers_list(conn: connection.Connection = Depends(get_openstack_connection)):
    try:
        servers = conn.compute.servers()
        server_list = [server.name for server in servers]
        return {"servers": server_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list server: {e}")
