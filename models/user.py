from sqlalchemy import Column, String, DateTime, Text, UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .database import Base
import uuid


class User(Base):
    __tablename__ = "user"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)  # This will store the hashed password
    color = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Project(Base):
    __tablename__ = "project"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    owner_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key to user
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    data = Column(JSONB, nullable=True)
