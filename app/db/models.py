from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class FileRecord(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    filename = Column(String, index=True)
    file_path = Column(String)
    original_crs = Column(String, nullable=True)
    measurement_crs = Column(String, nullable=True)
    feature_count = Column(Integer, default=0)
    status = Column(String, default="PROCESSING") # PROCESSING, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)

    features = relationship("FeatureRecord", back_populates="file_record", cascade="all, delete")

class FeatureRecord(Base):
    __tablename__ = "features"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    file_id = Column(String, ForeignKey("files.id"))
    feature_index = Column(Integer)
    geometry_type = Column(String)
    properties = Column(JSON, nullable=True)
    
    measurement_type = Column(String, nullable=True)
    measurement_value = Column(Float, nullable=True)
    measurement_unit = Column(String, nullable=True)
    message = Column(String, nullable=True)

    file_record = relationship("FileRecord", back_populates="features")
