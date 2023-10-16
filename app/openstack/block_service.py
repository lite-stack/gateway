from openstack import connection
from openstack.block_storage.v2.volume import Volume as OpenStackVolume


def create_volume(
        conn: connection.Connection,
        image: str,
        name: str,
        size: int = 20,
) -> OpenStackVolume:
    volume = conn.block_storage.create_volume(
        size=size,
        image_id=image,
        name=name,
    )
    conn.block_storage.wait_for_status(volume, status='available', failures=['error'], interval=2, wait=300)

    return volume


def get_block_device_mapping(volume: OpenStackVolume) -> dict[str]:
    return {
        "boot_index": "0",
        "uuid": volume.id,
        "source_type": "volume",
        "destination_type": "volume",
        "delete_on_termination": True
    }
