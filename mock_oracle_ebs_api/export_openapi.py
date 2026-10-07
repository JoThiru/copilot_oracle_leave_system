"""
Export OpenAPI JSON Specification from FastAPI app.
This file can be directly imported into Microsoft Power Platform (Power Automate & Copilot Studio)
to auto-generate Custom Connectors with all endpoints, request/response schemas.
"""

import json
import sys
from pathlib import Path

# Ensure project root is in sys.path so imports resolve in all environments
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mock_oracle_ebs_api.main import app

from fastapi.openapi.utils import get_openapi


def export_spec():
    openapi_schema = get_openapi(
        title="Oracle EBS Leave Assistant API",
        version="1.0.0",
        description="RESTful Mock APIs for Oracle E-Business Suite Leave Management System",
        routes=app.routes,
    )
    
    output_path = Path(__file__).resolve().parent / "openapi_spec.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    
    print(f"OpenAPI Specification exported successfully to: {output_path}")


if __name__ == "__main__":
    export_spec()
