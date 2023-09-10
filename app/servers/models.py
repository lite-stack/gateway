from sqlalchemy import Column, String, UUID, ForeignKey, ARRAY
from sqlalchemy.orm import relationship

from app.auth.models import Base


class Server(Base):
    __tablename__ = "server"
    openstack_id = Column(UUID, unique=True, nullable=False, primary_key=True)
    owner_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    owner = relationship("User", back_populates="servers")


class ServerConfig(Base):
    __tablename__ = "server_config"
    name = Column(String, unique=True, nullable=False, primary_key=True)
    description = Column(String, nullable=False)
    image = Column(String, nullable=False)
    flavor = Column(String, nullable=False)
    networks = Column(ARRAY(String))
