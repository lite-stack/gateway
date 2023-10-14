import datetime
import json
import uuid
from enum import Enum
from typing import Optional, Union

from openstack.compute.v2.flavor import Flavor as OpenStackFlavor
from openstack.compute.v2.image import Image as OpenStackImage
from openstack.compute.v2.server import Server as OpenStackServer
from openstack.network.v2.network import Network as OpenStackNetwork
from pydantic import BaseModel


class Flavor(BaseModel):
    name: str
    description: str
    ram: int
    vcpus: int
    disk_size: int
    swap_size: int
    ephemeral_size: int

    @classmethod
    def create_from_openstack(cls, flavor: OpenStackFlavor) -> 'Flavor':
        description = flavor.description or ""
        return cls(
            name=flavor.name,
            description=description,
            ram=flavor.ram,
            vcpus=flavor.vcpus,
            disk_size=flavor.disk,
            swap_size=flavor.swap,
            ephemeral_size=flavor.ephemeral,
        )


class Image(BaseModel):
    name: str
    min_disk_size: int
    min_ram_size: int
    status: str
    size: int
    created_at: str
    updated_at: str

    @classmethod
    def create_from_openstack(cls, image: OpenStackImage) -> Union['Image', None]:
        return cls(
            name=image.name,
            min_disk_size=image.min_disk,
            min_ram_size=image.min_ram,
            status=image.status,
            size=image.size,
            created_at=image.created_at,
            updated_at=image.updated_at,
        )


class Network(BaseModel):
    name: str
    description: str
    status: str
    is_default: bool
    created_at: str
    updated_at: str

    @classmethod
    def create_from_openstack(cls, network: OpenStackNetwork) -> 'Network':
        is_default = network.is_default or False
        return cls(
            name=network.name,
            description=network.description,
            status=network.status,
            is_default=is_default,
            created_at=network.created_at,
            updated_at=network.updated_at,
        )


class Volume(BaseModel):
    pass


class Server(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    openstack_user_id: uuid.UUID

    name: str
    status: str
    vm_state: str
    task_state: Optional[str] = ""

    launched_at: datetime.datetime
    terminated_at: Optional[datetime.datetime] = None

    ip_v4_public: str = ""
    ip_v4_private: str = ""
    ip_v6_public: str = ""
    ip_v6_private: str = ""

    @classmethod
    def create_from_openstack_server(cls, user_id: uuid.UUID, openstack_server: OpenStackServer) -> 'Server':
        ip_v4_public = ""
        ip_v6_public = ""
        ip_v4_private = ""
        ip_v6_private = ""

        for public_address in openstack_server.addresses.get('private', dict()):
            version = public_address.get('version', None)
            addr = public_address.get('addr', None)
            address_type = public_address.get('OS-EXT-IPS:type', '')
            if version == 4:
                if address_type == 'fixed':
                    ip_v4_private = addr
                elif address_type == 'floating':
                    ip_v4_public = addr
            elif version == 6:
                if address_type == 'fixed':
                    ip_v6_private= addr
                elif address_type == 'floating':
                    ip_v6_public = addr

        for private_address in openstack_server.addresses.get('shared', dict()):
            version = private_address.get('version', None)
            addr = private_address.get('addr', None)
            if version == 4:
                ip_v4_private = addr
            elif version == 6:
                ip_v6_private = addr

        return cls(
            user_id=user_id,
            id=openstack_server.id,
            openstack_user_id=openstack_server.user_id,
            name=openstack_server.name,
            status=openstack_server.status,
            vm_state=openstack_server.vm_state,
            task_state=openstack_server.task_state,
            launched_at=openstack_server.launched_at,
            terminated_at=openstack_server.terminated_at,
            ip_v4_public=ip_v4_public,
            ip_v6_public=ip_v6_public,
            ip_v4_private=ip_v4_private,
            ip_v6_private=ip_v6_private,
        )


class ServerDetailed(Server):
    description: Optional[str] = ""

    flavor: Optional[Flavor] = None
    image: Optional[Image] = None
    volumes: Optional[list[Volume]] = None

    created_at: datetime.datetime
    updated_at: datetime.datetime

    metadata: str
    full_info: str

    @classmethod
    def create_from_openstack_server(
            cls,
            user_id: uuid.UUID,
            openstack_server: OpenStackServer,
            openstack_image: Optional[OpenStackImage] = None,
    ) -> 'ServerDetailed':
        server = Server.create_from_openstack_server(user_id, openstack_server)
        image = None
        if openstack_image:
            image = Image.create_from_openstack(image=openstack_image)

        return cls(
            **server.model_dump(),
            description=openstack_server.description,
            flavor=Flavor.create_from_openstack(flavor=openstack_server.flavor),
            image=image,
            volumes=[Volume()],
            created_at=openstack_server.created_at,
            updated_at=openstack_server.updated_at,
            metadata=json.dumps(openstack_server.metadata),
            full_info=json.dumps(openstack_server.to_dict()),
        )


class ServerConfiguration(BaseModel):
    name: str
    description: str
    flavor: str
    image: str
    networks: list[str]


class ServerStateActionEnum(str, Enum):
    pause = "pause"
    unpause = "unpause"
    start = "start"
    stop = "stop"
    reboot = "reboot"


class ServerStateActionUpdate(BaseModel):
    action: ServerStateActionEnum


class ServeCreate(BaseModel):
    name: str
    description: str
    configuration_name: str


class ServeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
