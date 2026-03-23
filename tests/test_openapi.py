from __future__ import annotations

from typing import Any

import pytest
from app.core.openapi_config import OPENAPI_TAGS
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def api_client() -> TestClient:
    return TestClient(app)


def test_openapi_json_ok(api_client: TestClient) -> None:
    response = api_client.get("/openapi.json")
    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("application/json")
    data = response.json()
    assert data["openapi"].startswith("3.")
    assert data["info"]["title"] == "LBC API"
    assert data["info"]["version"] == "0.5.0"
    assert "MIT" in (data["info"].get("license") or {}).get("name", "")


def test_openapi_paths_and_methods(api_client: TestClient) -> None:
    paths: dict[str, Any] = api_client.get("/openapi.json").json()["paths"]
    assert "/health" in paths
    assert "get" in paths["/health"]
    assert "/v1/search" in paths
    assert "post" in paths["/v1/search"]
    assert "/v1/search/with-users" in paths
    assert "/v1/ads/{ad_id}" in paths
    assert "/v1/ads/batch" in paths
    assert "/v1/users/{user_id}" in paths
    assert "/v1/search/cars" in paths
    assert "/v1/search/real-estate" in paths
    assert "/v1/schemas/search-cars" in paths
    assert "/v1/schemas/search-real-estate" in paths


def test_openapi_tags_match_config(api_client: TestClient) -> None:
    doc = api_client.get("/openapi.json").json()
    configured = {t["name"] for t in OPENAPI_TAGS}
    declared = {t["name"] for t in doc.get("tags", [])}
    assert configured == declared


def test_openapi_operation_ids_stable(api_client: TestClient) -> None:
    paths: dict[str, Any] = api_client.get("/openapi.json").json()["paths"]
    health_op = paths["/health"]["get"].get("operationId", "")
    assert health_op == "Health-health"
    search_op = paths["/v1/search"]["post"].get("operationId", "")
    assert search_op == "Search-post_search"


def test_swagger_ui_served(api_client: TestClient) -> None:
    response = api_client.get("/docs")
    assert response.status_code == 200
    body = response.text.lower()
    assert "swagger" in body or "openapi" in body


def test_redoc_served(api_client: TestClient) -> None:
    response = api_client.get("/redoc")
    assert response.status_code == 200
    assert "redoc" in response.text.lower()


def test_schema_search_cars_json_includes_vehicle_filters(api_client: TestClient) -> None:
    response = api_client.get("/v1/schemas/search-cars")
    assert response.status_code == 200
    schema = response.json()
    assert schema.get("title") == "SearchCarsBody"
    defs = schema.get("$defs", {})
    assert "VehicleFilters" in defs
    props = defs["VehicleFilters"].get("properties", {})
    assert "u_car_brands" in props
    assert "critair" in props


def test_schema_search_real_estate_json_includes_real_estate_filters(
    api_client: TestClient,
) -> None:
    response = api_client.get("/v1/schemas/search-real-estate")
    assert response.status_code == 200
    schema = response.json()
    assert schema.get("title") == "SearchRealEstateBody"
    defs = schema.get("$defs", {})
    assert "RealEstateFilters" in defs
    ref_props = defs["RealEstateFilters"].get("properties", {})
    assert "real_estate_types" in ref_props
    assert "energy_rates" in ref_props
