from openstack.compute.v2.server import Server as OpenStackServer
def get_os_default_user(image: str):
    match image.split("-"):
        case ["cirros", *_, ]:
            return "cirros"
        case ["ubuntu", *_,]:
            return "ubuntu"
        case ["centos", *_]:
            return "centos"
        case ["debian", *_]:
            return "debian"
        case ["Fedora", *_]:
            return "fedora"
        case ["arch", *_]:
            return "arch"
        case _:
            return "root"

def get_server_public_ip(server: OpenStackServer) -> str:
    for public_address in server.addresses.get('private', dict()):
        version = public_address.get('version', None)
        addr = public_address.get('addr', None)
        address_type = public_address.get('OS-EXT-IPS:type', '')
        if version == 4 and address_type == 'floating':
           return addr

    return ""