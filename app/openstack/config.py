import openstack

from app.config import settings

# Initialize and turn on debug logging
openstack.enable_logging(debug=True)


# Initialize connection
async def get_connection():
    return openstack.connect(cloud=settings.cloud_name)
