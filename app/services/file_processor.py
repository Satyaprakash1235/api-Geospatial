import os
import shutil
import zipfile
import tempfile
import logging
import geopandas as gpd
from fastapi import HTTPException
from app.core.config import settings

logger = logging.getLogger(__name__)

def validate_and_save_file(upload_file, file_id: str) -> str:
    """Validates the file extension and saves it."""
    ext = os.path.splitext(upload_file.filename)[1].lower()
    if ext not in ['.kml', '.zip']:
        raise HTTPException(status_code=400, detail="Only .kml and .zip files are supported")
    
    # Save file
    safe_filename = f"{file_id}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    # File size validation could be added here
    file_size = os.path.getsize(file_path)
    if file_size > settings.MAX_UPLOAD_SIZE:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="File too large")
        
    return file_path

def process_geospatial_file(file_path: str):
    """Reads the geospatial file into a GeoDataFrame."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.kml':
        try:
            import fiona
            fiona.drvsupport.supported_drivers['KML'] = 'rw'
            gdf = gpd.read_file(file_path, driver='KML')
            return gdf
        except Exception as e:
            logger.error(f"Error reading KML: {e}")
            raise HTTPException(status_code=400, detail="Invalid KML file or parsing error")
            
    elif ext == '.zip':
        try:
            # Prevent Zip Slip and find .shp safely
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        # Zip Slip validation
                        for member in zip_ref.namelist():
                            if member.startswith('/') or '..' in member:
                                raise HTTPException(status_code=400, detail="Invalid ZIP contents (path traversal detected)")
                        
                        zip_ref.extractall(temp_dir)
                except zipfile.BadZipFile:
                    raise HTTPException(status_code=400, detail="Invalid ZIP format")
                
                # Find .shp and ensure .shx and .dbf exist
                shp_path = None
                has_shx = False
                has_dbf = False
                
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith('.shp'):
                            shp_path = os.path.join(root, file)
                        elif file.endswith('.shx'):
                            has_shx = True
                        elif file.endswith('.dbf'):
                            has_dbf = True
                            
                if not shp_path or not has_shx or not has_dbf:
                    raise HTTPException(status_code=400, detail="ZIP file must contain .shp, .shx, and .dbf files")
                
                # Read Shapefile
                gdf = gpd.read_file(shp_path)
                return gdf
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reading ZIP/Shapefile: {e}")
            raise HTTPException(status_code=400, detail="Error reading Shapefile from ZIP")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")
