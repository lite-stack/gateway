import os

from openstack.compute.v2.keypair import Keypair as OpenStackKeypair
from openstack.compute.v2.server import Server as OpenStackServer
from starlette.background import BackgroundTasks

from app.auth.models import User
from app.mailing.service import send_email


def generate_file(path: str, data: str) -> str:
    with open(path, 'w') as file:
        file.write(data)

    return path


def delete_file(path: str):
    try:
        os.remove(path)
    except OSError:
        pass


async def send_keypair_email(
        background_tasks: BackgroundTasks,
        user: User,
        key_pair: OpenStackKeypair,
        server: OpenStackServer,
):
    private_file_path = generate_file(f'./temp/{user.id}_devstask', key_pair.private_key)
    public_file_path = generate_file(f'./temp/{user.id}_devstask.pub', key_pair.public_key)

    ip_v4_public = ''
    for public_address in server.addresses.get('public', dict()):
        version = public_address.get('version', None)
        addr = public_address.get('addr', None)
        if version == 4:
            ip_v4_public = addr

    if not ip_v4_public:
        return

    await send_email(
        background_tasks,
        "LiteStack: your private ssg key",
        user.email,
        {'public_address': ip_v4_public},
        [
            {
                "file": private_file_path,
                "headers": {
                    "Content-Disposition": "attachment; filename=\"devstack\"",
                },
                "mime_type": "text",
                "mime_subtype": "plain",
            },
            {
                "file": public_file_path,
                "headers": {
                    "Content-Disposition": "attachment; filename=\"devstack.pub\"",
                },
                "mime_type": "text",
                "mime_subtype": "plain",
            },
        ],
        "ssh_email.html",
    )

    delete_file(private_file_path)
    delete_file(public_file_path)
