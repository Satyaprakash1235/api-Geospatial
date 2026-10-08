import logging
from pyproj import CRS

logger = logging.getLogger(__name__)

def determine_projected_crs(gdf):
    """
    Determine an appropriate projected CRS for a given GeoDataFrame.
    If the current CRS is already projected, return it.
    If geographic, determine an appropriate UTM CRS based on the dataset's centroid.
    """
    if gdf.crs is None:
        logger.warning("No CRS found in GeoDataFrame.")
        return None
    
    if gdf.crs.is_projected:
        logger.info(f"Input CRS {gdf.crs.to_string()} is already projected.")
        return gdf.crs.to_string()
    
    if gdf.crs.is_geographic:
        logger.info(f"Input CRS {gdf.crs.to_string()} is geographic. Determining UTM zone.")
        try:
            projected_crs = gdf.estimate_utm_crs()
            crs_str = projected_crs.to_string()
            logger.info(f"Determined projected CRS: {crs_str}")
            return crs_str
        except Exception as e:
            logger.error(f"Error determining projected CRS: {e}")
            return None
    
    logger.warning("Input CRS is neither explicitly geographic nor projected, but assuming it needs projection.")
    return None
