import pytest
import geopandas as gpd
from shapely.geometry import Point
from app.services.crs import determine_projected_crs

def test_determine_projected_crs_already_projected():
    # EPSG:32643 is already projected
    gdf = gpd.GeoDataFrame(geometry=[Point(0, 0)], crs="EPSG:32643")
    crs = determine_projected_crs(gdf)
    assert crs == "EPSG:32643"

def test_determine_projected_crs_geographic():
    # EPSG:4326 is geographic, and a point near Bengaluru (12.97, 77.59)
    # UTM zone = int((77.59 + 180) / 6) + 1 = int(257.59 / 6) + 1 = 42 + 1 = 43
    # Northern hemisphere, so 32600 + 43 = 32643
    gdf = gpd.GeoDataFrame(geometry=[Point(77.59, 12.97)], crs="EPSG:4326")
    crs = determine_projected_crs(gdf)
    assert crs == "EPSG:32643"

def test_determine_projected_crs_missing():
    gdf = gpd.GeoDataFrame(geometry=[Point(0, 0)])
    # crs is None by default
    crs = determine_projected_crs(gdf)
    assert crs is None
