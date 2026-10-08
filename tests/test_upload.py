import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
import zipfile
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point
import io

client = TestClient(app)

@pytest.fixture(scope="session")
def sample_kml():
    kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Test Polygon</name>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              77.5946,12.9716,0
              77.5947,12.9716,0
              77.5947,12.9717,0
              77.5946,12.9717,0
              77.5946,12.9716,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>
"""
    return kml_content

def test_invalid_extension():
    response = client.post(
        "/api/files/",
        files={"file": ("test.txt", b"hello", "text/plain")}
    )
    assert response.status_code == 400
    assert "Only .kml and .zip files are supported" in response.json()["detail"]

def test_upload_kml(sample_kml):
    response = client.post(
        "/api/files/",
        files={"file": ("test.kml", sample_kml.encode("utf-8"), "application/vnd.google-earth.kml+xml")}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.kml"
    assert data["status"] == "COMPLETED"
    assert data["feature_count"] == 1

def test_upload_corrupted_zip():
    response = client.post(
        "/api/files/",
        files={"file": ("test.zip", b"PK12345", "application/zip")}
    )
    assert response.status_code == 400
    assert "Invalid ZIP format" in response.json()["detail"]

def test_upload_zip_no_shapefile():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr("test.txt", b"hello")
    
    response = client.post(
        "/api/files/",
        files={"file": ("test.zip", zip_buffer.getvalue(), "application/zip")}
    )
    assert response.status_code == 400
    assert "ZIP file must contain .shp, .shx, and .dbf files" in response.json()["detail"]
