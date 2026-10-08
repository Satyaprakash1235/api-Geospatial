from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict

class Measurement(BaseModel):
    type: str
    value: float
    unit: str
    
    model_config = ConfigDict(from_attributes=True)

class FeatureMeasurement(BaseModel):
    feature_id: int
    geometry_type: str
    crs: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    measurement: Optional[Measurement] = None
    status: Optional[str] = None
    message: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class FileUploadResponse(BaseModel):
    id: str
    filename: str
    feature_count: int
    crs: Optional[str]
    status: str
    
    model_config = ConfigDict(from_attributes=True)

class FileInfoResponse(BaseModel):
    id: str
    filename: str
    feature_count: int
    crs: Optional[str]
    status: str
    file_type: str
    
    model_config = ConfigDict(from_attributes=True)

class MeasurementResponse(BaseModel):
    file_id: str
    filename: Optional[str] = None
    original_crs: Optional[str] = None
    measurement_crs: Optional[str] = None
    features: List[FeatureMeasurement]
    
    model_config = ConfigDict(from_attributes=True)
