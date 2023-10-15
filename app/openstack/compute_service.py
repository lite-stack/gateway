import time

from openstack import connection
from openstack.compute.v2.flavor import Flavor as OpenStackFlavor
from openstack.compute.v2.image import Image as OpenStackImage
from openstack.compute.v2.keypair import Keypair as OpenStackKeypair
from openstack.compute.v2.server import Server as OpenStackServer
from openstack.network.v2.floating_ip import FloatingIP as OpenstackFloatingIP

import app.openstack.network_service as network_service
from app.config import settings
from app.servers.models import ServerConfig

def create_server(
        conn: connection.Connection,
        user_id: str,
        name: str,
        description: str,
        server_config: ServerConfig,
) -> (OpenStackServer, OpenStackKeypair, OpenstackFloatingIP):
    image = conn.image.find_image(server_config.image)
    flavor = conn.compute.find_flavor(server_config.flavor)

    networks = []
    for network in server_config.networks:
        openstack_network = network_service.get_network(conn, network)
        networks.append({"uuid": openstack_network.id})

    keypair = create_keypair(conn, user_id)

    server = conn.compute.create_server(
        name=name,
        description=description,
        admin_password=name,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=networks,
        key_name=keypair.name,
        disk_config="AUTO",
    )
    conn.compute.wait_for_server(server)
    ip_address = network_service.create_floating_ip_and_assign_to_server(conn, server)
    return server, keypair, ip_address

def add_floating_ip_to_server(conn:connection.Connection, server: OpenStackServer, floating_ip: OpenstackFloatingIP):
    conn.compute.add_floating_ip_to_server(server, floating_ip)

def create_keypair(conn: connection.Connection, name) -> OpenStackKeypair:
    keypair = conn.compute.find_keypair(name)

    if not keypair:
        keypair = conn.compute.create_keypair(name=name)

    return keypair
def create_floating_ip(conn: connection.Connection, network_id: str) -> OpenstackFloatingIP:
    return conn.network.create_ip(floating_network_id=network_id)


def get_all_servers(conn: connection.Connection) -> list[OpenStackServer]:
    return conn.compute.servers(all_projects=True)


def get_servers_by_ids(conn: connection.Connection, ids: list[str]) -> list[OpenStackServer]:
    servers = []
    for server_id in ids:
        server = conn.compute.find_server(server_id)
        if server:
            servers.append(server)
        else:
            print(f"Server with ID {server_id} not found.")

    return servers


def get_server(conn: connection.Connection, server_id: str) -> OpenStackServer:
    return conn.compute.find_server(server_id)

def create_server_console(conn, server_id: str) -> dict[str]:
    return conn.compute.create_console(server_id, "novnc")

def update_server(
        conn: connection.Connection,
        server_id: str,
        name: str,
        description: str,
):
    data = {}
    if name:
        data["name"] = name

    if description:
        data["description"] = description

    conn.compute.update_server(server_id, **data)


def delete_server(conn: connection.Connection, server_id: str):
    conn.compute.delete_server(server_id, ignore_missing=True)


def pause_server(conn: connection.Connection, server_id: str):
    conn.compute.pause_server(server_id)


def unpause_server(conn: connection.Connection, server_id: str):
    conn.compute.unpause_server(server_id)


def start_server(conn: connection.Connection, server_id: str):
    conn.compute.start_server(server_id)


def stop_server(conn: connection.Connection, server_id: str):
    conn.compute.stop_server(server_id)


def reboot_server(conn: connection.Connection, server_id: str):
    conn.compute.reboot_server(server_id, reboot_type="HARD")


def get_flavors(conn: connection.Connection) -> list[OpenStackFlavor]:
    return conn.compute.flavors()


def get_images(conn: connection.Connection) -> list[OpenStackImage]:
    return conn.compute.images()


def get_image(conn: connection.Connection, image_id: str) -> list[OpenStackImage]:
    return conn.compute.find_image(image_id)

def get_instance_limit(conn: connection.Connection) -> int:
    limits = conn.compute.get_limits()
    max_server_limit =limits.absolute['maxTotalInstances']
    return min(max_server_limit, settings.max_server_limit)