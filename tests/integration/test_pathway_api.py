
from decimal import Decimal

from fastapi.testclient import TestClient

from aditi.api.main import create_app

client = TestClient(create_app())


def sample_pathway() -> dict:
    """Return a minimal valid pathway definition."""

    return {
        "name": "Glycolysis Test Pathway",
        "description": "A minimal pathway for API testing.",
        "metabolites": [
            {
                "id": "glucose",
                "name": "Glucose",
                "chemical_formula": "C6H12O6",
                "charge": 0,
            },
            {
                "id": "glucose-6-phosphate",
                "name": "Glucose 6-phosphate",
                "chemical_formula": "C6H13O9P",
                "charge": -2,
            },
        ],
        "reactions": [
            {
                "id": "hexokinase",
                "name": "Hexokinase",
                "reactants": [
                    {
                        "metabolite_id": "glucose",
                        "coefficient": "1",
                    },
                ],
                "products": [
                    {
                        "metabolite_id": "glucose-6-phosphate",
                        "coefficient": "1",
                    },
                ],
                "reversible": False,
            },
        ],
    }


def test_health_endpoint_returns_success():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "application": "Aditi",
        "status": "ok",
    }


def test_layout_endpoint_returns_available_layouts():
    response = client.get("/api/v1/pathways/layouts")

    assert response.status_code == 200

    layouts = response.json()["layouts"]

    assert "hierarchical" in layouts
    assert "force-directed" in layouts


def test_visualization_endpoint_builds_pathway_scene():
    response = client.post(
        "/api/v1/pathways/visualize",
        json=sample_pathway(),
    )

    assert response.status_code == 200

    result = response.json()

    assert "pathway_identity" in result
    assert len(result["nodes"]) == 3
    assert len(result["edges"]) == 2

    assert {
        node["label"]
        for node in result["nodes"]
    } == {
        "Glucose",
        "Glucose 6-phosphate",
        "Hexokinase",
    }


def test_visualization_endpoint_supports_force_directed_layout():
    response = client.post(
        "/api/v1/pathways/visualize?layout_id=force-directed",
        json=sample_pathway(),
    )

    assert response.status_code == 200
    assert len(response.json()["nodes"]) == 3


def test_visualization_endpoint_rejects_unknown_layout():
    response = client.post(
        "/api/v1/pathways/visualize?layout_id=unknown-layout",
        json=sample_pathway(),
    )

    assert response.status_code == 400


def test_visualization_endpoint_rejects_unknown_metabolite_reference():
    definition = sample_pathway()

    definition["reactions"][0]["reactants"][0]["metabolite_id"] = (
        "unknown-metabolite"
    )

    response = client.post(
        "/api/v1/pathways/visualize",
        json=definition,
    )

    assert response.status_code == 422


def test_visualization_endpoint_rejects_invalid_payload():
    definition = sample_pathway()
    definition["metabolites"] = []

    response = client.post(
        "/api/v1/pathways/visualize",
        json=definition,
    )

    assert response.status_code == 422


def test_visualization_endpoint_preserves_stoichiometric_coefficients():
    definition = sample_pathway()

    definition["reactions"][0]["reactants"][0]["coefficient"] = "2"

    response = client.post(
        "/api/v1/pathways/visualize",
        json=definition,
    )

    assert response.status_code == 200

    coefficients = [
        Decimal(edge["coefficient"])
        for edge in response.json()["edges"]
    ]

    assert Decimal(2) in coefficients


def test_openapi_schema_is_available():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/pathways/layouts" in schema["paths"]
    assert "/api/v1/pathways/visualize" in schema["paths"]
