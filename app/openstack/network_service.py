from openstack import connection
from openstack.network.v2.network import Network as OpenStackNetwork


def get_networks(conn: connection.Connection) -> list[OpenStackNetwork]:
    return conn.network.networks()
