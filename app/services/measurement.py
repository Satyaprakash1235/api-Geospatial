import logging
from shapely.geometry.base import BaseGeometry

logger = logging.getLogger(__name__)

def calculate_measurement(geom: BaseGeometry, geom_type: str):
    """
    Calculate measurement based on geometry type.
    """
    if geom is None or geom.is_empty:
        return None, "Geometry is empty or invalid"
    
    if geom_type in ["Polygon", "MultiPolygon"]:
        value = round(geom.area, 2)
        return {"type": "area", "value": value, "unit": "m²"}, None
    
    elif geom_type in ["LineString", "MultiLineString"]:
        value = round(geom.length, 2)
        return {"type": "length", "value": value, "unit": "m"}, None
    
    elif geom_type in ["Point", "MultiPoint"]:
        return None, None  # Points don't have area/length
    
    else:
        return None, f"Measurement not supported for this geometry type: {geom_type}"
