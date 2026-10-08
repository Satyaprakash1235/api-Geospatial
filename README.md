# api-Geospatial

## Project Overview
Geospatial File Measurement API is a production-ready RESTful service built with FastAPI that accepts geospatial files (`.kml` and `.zip` containing Shapefiles), processes their features, manages Coordinate Reference Systems (CRS) dynamically, and calculates physical measurements such as Area (for Polygons) and Length (for LineStrings).

## Features
- KML upload
- Shapefile ZIP upload
- Feature extraction
- CRS handling
- Polygon area calculation
- LineString length calculation
- Point handling
- Error handling
- SQLite persistence
- API documentation (Swagger)
- Tests
- Docker support

## Tech Stack
- **Python 3.11+**: Primary language.
- **FastAPI**: Modern, fast web framework for building APIs.
- **Uvicorn**: Lightning-fast ASGI server.
- **GeoPandas & Shapely**: For robust geospatial data processing and geometric calculations.
- **PyProj**: For Coordinate Reference System (CRS) transformations.
- **SQLite & SQLAlchemy**: Relational database mapping and storage.
- **Pytest**: Testing framework.
- **Docker**: Containerization.

## Architecture

```text
Client
  ↓
FastAPI
  ↓
File Validation
  ↓
GeoPandas
  ↓
CRS Processing
  ↓
Shapely Measurements
  ↓
SQLite
  ↓
JSON Response
```

## Project Structure
- `app/api/`: Contains the FastAPI routes.
- `app/core/`: Configuration and settings.
- `app/db/`: Database models and session management.
- `app/schemas/`: Pydantic response models.
- `app/services/`: Business logic (File processing, CRS handling, Measurements).
- `tests/`: Pytest suite.

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running Locally

```bash
uvicorn app.main:app --reload
```

## API Usage

1. **Upload a File**
```bash
curl -X POST http://localhost:8000/api/files/ -F "file=@sample.kml"
```

2. **Get File Info**
```bash
curl -X GET http://localhost:8000/api/files/{id}/
```

3. **Get File Measurements**
```bash
curl -X GET http://localhost:8000/api/files/{id}/measurements/
```

## Example Response

```json
{
  "file_id": "abc12345",
  "filename": "sample.kml",
  "original_crs": "EPSG:4326",
  "measurement_crs": "EPSG:32643",
  "features": [
    {
      "feature_id": 0,
      "geometry_type": "Polygon",
      "properties": {
        "name": "Survey Area"
      },
      "measurement": {
        "type": "area",
        "value": 125430.52,
        "unit": "m²"
      }
    }
  ]
}
```

## CRS Handling
Using geographic coordinate systems (like EPSG:4326 - latitude/longitude) directly for area or length measurements results in degrees, which is physically meaningless.
To properly measure area and distance, the API dynamically determines a projected CRS (Universal Transverse Mercator - UTM) based on the dataset's centroid.
- If already projected, it uses the input CRS.
- If geographic, it determines the correct UTM zone and transforms the geometries before measurement.

## Design Decisions
- **FastAPI**: Provides built-in async capabilities, easy validation with Pydantic, and automatic Swagger docs.
- **GeoPandas/Shapely**: Industry standard for Python geospatial data handling.
- **SQLite**: Simple, zero-configuration database perfect for the assignment requirements.
- **Modular Architecture**: Separates routing from business logic (services) and database interactions, making testing and scaling easier.

## Error Handling
Graceful error handling is implemented via FastAPI HTTPExceptions. 
Unsupported geometries inside a dataset will result in a null measurement with a message, rather than failing the whole file. Missing CRS, invalid ZIPs, and unsupported extensions all return clear 400 Bad Request responses.

## Security
- **ZIP Validation and Zip Slip**: The extraction process prevents Zip Slip path traversal attacks by validating member filenames.
- **Safe Extraction**: Files are extracted to a temporary directory context.
- **File Size Limits**: Max upload sizes are configurable to avoid overwhelming the server.
- **Error Obfuscation**: Internal stack traces are logged but not exposed to API clients.

## Testing
Run tests using:
```bash
pytest
```

## Docker

Build image:
```bash
docker build -t geospatial-measurement-api .
```

Run container:
```bash
docker run -p 8000:8000 geospatial-measurement-api
```

Alternatively using docker-compose:
```bash
docker-compose up --build
```

## Learning
This project demonstrates applying robust Backend Software Engineering principles to Geospatial data. It includes handling complex geometries, understanding EPSG projections vs geographic coordinate systems, preventing path traversal attacks, and utilizing modern async Python capabilities with FastAPI.

## Future Scope
- Support for GeoJSON and GeoPackage.
- Move to PostGIS for database-level spatial operations.
- Integrate Celery and Redis for asynchronous background processing.
- Add user authentication and rate limiting.
