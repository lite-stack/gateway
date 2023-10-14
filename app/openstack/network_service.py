from typing import Optional

from openstack import connection
from openstack.network.v2.network import Network as OpenStackNetwork
from openstack.network.v2.floating_ip import FloatingIP as OpenstackFloatingIP
from openstack.compute.v2.server import Server as OpenStackServer

PUBLIC_NETWORK_NAME='public'

def get_networks(conn: connection.Connection) -> list[OpenStackNetwork]:
    return conn.network.networks()


def get_network(conn: connection.Connection, network_name: str) -> OpenstackFloatingIP:
    return conn.network.find_network(name_or_id=network_name, ignore_missing=False)


def create_floating_ip_and_assign_to_server(
        conn:  connection.Connection,
        server: OpenStackServer,
        floating_network_name: str=PUBLIC_NETWORK_NAME,
) -> Optional[OpenstackFloatingIP]:
    floating_network = conn.network.find_network(floating_network_name)

    server_ports = conn.network.ports(device_id=server.id)
    server_ports = list(server_ports)
    if server_ports and len(server_ports) > 0:
        server_port = server_ports[0]
        floating_ip = conn.network.create_ip(floating_network_id=floating_network.id, port_id=server_port.id)
        return floating_ip
    else:
        return None