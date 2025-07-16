import json
import os
from src.api.main import app

"""
Script to generate OpenAPI spec (openapi.json) for the FastAPI backend API.

Usage:
    Run this script from the backend_fastapi directory:
        python3 src/api/generate_openapi.py

Effect:
    Will output/overwrite:
        interfaces/openapi.json
    with the latest OpenAPI documentation reflecting all current routers, endpoints, models, and schemas.
"""

# Obtain the OpenAPI schema from app
openapi_schema = app.openapi()

# Output directory for the OpenAPI spec
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../interfaces")
output_dir = os.path.normpath(output_dir)
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "openapi.json")
with open(output_path, "w") as f:
    json.dump(openapi_schema, f, indent=2)

print(f"OpenAPI schema written to: {output_path}")
