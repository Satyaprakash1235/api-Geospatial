from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
import math
import logging
from app.db.database import get_db
from app.db import models
from app.schemas.file import FileUploadResponse, FileInfoResponse, MeasurementResponse, FeatureMeasurement, Measurement
from app.services.file_processor import validate_and_save_file, process_geospatial_file
from app.services.crs import determine_projected_crs
from app.services.measurement import calculate_measurement

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/files/", response_model=FileUploadResponse, status_code=201)
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info(f"Uploading file: {file.filename}")
    
    # 1. Create file record
    file_id = str(uuid.uuid4())
    
    # 2. Validate and save
    file_path = validate_and_save_file(file, file_id)
    
    db_file = models.FileRecord(
        id=file_id,
        filename=file.filename,
        file_path=file_path,
        status="PROCESSING"
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    try:
        # 3. Process Geospatial File
        logger.info(f"Processing geospatial file: {file_id}")
        gdf = process_geospatial_file(file_path)
        
        # 4. Check CRS
        original_crs = gdf.crs.to_string() if gdf.crs else None
        db_file.original_crs = original_crs
        
        projected_crs = determine_projected_crs(gdf)
        if not projected_crs:
            db_file.status = "FAILED"
            db.commit()
            raise HTTPException(status_code=400, detail="Could not determine projected CRS or CRS is missing")
            
        db_file.measurement_crs = projected_crs
        
        # Transform CRS if needed
        if original_crs != projected_crs:
            logger.info(f"Transforming CRS from {original_crs} to {projected_crs}")
            gdf = gdf.to_crs(projected_crs)
            
        # 5. Extract Features and Calculate Measurements
        feature_count = len(gdf)
        db_file.feature_count = feature_count
        
        for index, row in gdf.iterrows():
            geom = row.geometry
            geom_type = geom.geom_type if geom else "Unknown"
            
            # Extract non-geometry properties
            properties = row.drop('geometry').to_dict()
            # Replace NaNs with None for JSON serialization
            properties = {k: (None if (isinstance(v, float) and math.isnan(v)) else v) for k, v in properties.items()}
            
            measurement, message = calculate_measurement(geom, geom_type)
            
            db_feature = models.FeatureRecord(
                file_id=file_id,
                feature_index=index,
                geometry_type=geom_type,
                properties=properties,
            )
            
            if measurement:
                db_feature.measurement_type = measurement['type']
                db_feature.measurement_value = measurement['value']
                db_feature.measurement_unit = measurement['unit']
            
            if message:
                db_feature.message = message
                
            db.add(db_feature)
            
        db_file.status = "COMPLETED"
        db.commit()
        logger.info(f"File processing completed: {file_id}")
        
    except HTTPException:
        db_file.status = "FAILED"
        db.commit()
        raise
    except Exception as e:
        logger.error(f"Processing failed for file {file_id}: {e}")
        db_file.status = "FAILED"
        db.commit()
        raise HTTPException(status_code=500, detail="Unexpected processing failure")
        
    return FileUploadResponse(
        id=db_file.id,
        filename=db_file.filename,
        feature_count=db_file.feature_count,
        crs=db_file.original_crs,
        status=db_file.status
    )

@router.get("/files/{id}/", response_model=FileInfoResponse)
def get_file_info(id: str, db: Session = Depends(get_db)):
    db_file = db.query(models.FileRecord).filter(models.FileRecord.id == id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    ext = ".zip" if db_file.filename.endswith(".zip") else ".kml"
    
    return FileInfoResponse(
        id=db_file.id,
        filename=db_file.filename,
        feature_count=db_file.feature_count,
        crs=db_file.original_crs,
        status=db_file.status,
        file_type=ext
    )

@router.get("/files/{id}/measurements/", response_model=MeasurementResponse)
def get_measurements(id: str, db: Session = Depends(get_db)):
    db_file = db.query(models.FileRecord).filter(models.FileRecord.id == id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    features = db.query(models.FeatureRecord).filter(models.FeatureRecord.file_id == id).all()
    
    feature_responses = []
    for f in features:
        measurement = None
        if f.measurement_type:
            measurement = Measurement(
                type=f.measurement_type,
                value=f.measurement_value,
                unit=f.measurement_unit
            )
            
        feature_responses.append(FeatureMeasurement(
            feature_id=f.feature_index,
            geometry_type=f.geometry_type,
            crs=db_file.original_crs,
            properties=f.properties,
            measurement=measurement,
            status="COMPLETED" if db_file.status == "COMPLETED" else db_file.status,
            message=f.message
        ))
        
    return MeasurementResponse(
        file_id=db_file.id,
        filename=db_file.filename,
        original_crs=db_file.original_crs,
        measurement_crs=db_file.measurement_crs,
        features=feature_responses
    )
