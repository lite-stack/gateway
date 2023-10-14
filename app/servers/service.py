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
        ip_address: str,
        default_user: str,
):
    if not ip_address:
        return

    private_file_path = generate_file(f'./temp/{user.id}_devstask', key_pair.private_key)
    public_file_path = generate_file(f'./temp/{user.id}_devstask.pub', key_pair.public_key)

    await send_email(
        background_tasks,
        "LiteStack: your private ssh key",
        user.email,
        {
            'public_address': ip_address,
            'default_user': default_user,
        },
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
            {
                "file": "./templates/logo.png",
                "headers": {
                    "Content-ID": "<logo_image@fastapi-mail>",
                    "Content-Disposition": "inline; filename=\"file.png\"",  # For inline images only
                },
                "mime_type": "image",
                "mime_subtype": "png",
            }
        ],
        "ssh_email.html",
    )

    delete_file(private_file_path)
    delete_file(public_file_path)
