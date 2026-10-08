from shapely.geometry import Polygon, LineString, Point, GeometryCollection
from app.services.measurement import calculate_measurement

def test_polygon_area():
    # A 10x10 square
    poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])
    measurement, error = calculate_measurement(poly, "Polygon")
    assert error is None
    assert measurement["type"] == "area"
    assert measurement["value"] == 100.0
    assert measurement["unit"] == "m²"

def test_linestring_length():
    # A line of length 10
    line = LineString([(0, 0), (10, 0)])
    measurement, error = calculate_measurement(line, "LineString")
    assert error is None
    assert measurement["type"] == "length"
    assert measurement["value"] == 10.0
    assert measurement["unit"] == "m"

def test_point_handling():
    pt = Point(0, 0)
    measurement, error = calculate_measurement(pt, "Point")
    assert error is None
    assert measurement is None

def test_unsupported_geometry():
    gc = GeometryCollection([Point(0, 0)])
    measurement, error = calculate_measurement(gc, "GeometryCollection")
    assert error is not None
    assert "Measurement not supported" in error
    assert measurement is None
