from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from aditi.api.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


@pytest.fixture
def sbml_document() -> bytes:
    return b"""<?xml version="1.0" encoding="UTF-8"?>
    <sbml
        xmlns="http://www.sbml.org/sbml/level3/version2/core"
        level="3"
        version="2"
    >
        <model id="api_test_model" name="API Test Pathway">
            <listOfSpecies>
                <species
                    id="glucose"
                    name="Glucose"
                    compartment="cell"
                    boundaryCondition="false"
                    hasOnlySubstanceUnits="false"
                    constant="false"
                />
                <species
                    id="pyruvate"
                    name="Pyruvate"
                    compartment="cell"
                    boundaryCondition="false"
                    hasOnlySubstanceUnits="false"
                    constant="false"
                />
            </listOfSpecies>

            <listOfReactions>
                <reaction
                    id="glycolysis"
                    name="Glucose Conversion"
                    reversible="false"
                >
                    <listOfReactants>
                        <speciesReference
                            species="glucose"
                            stoichiometry="1"
                        />
                    </listOfReactants>

                    <listOfProducts>
                        <speciesReference
                            species="pyruvate"
                            stoichiometry="2"
                        />
                    </listOfProducts>
                </reaction>
            </listOfReactions>
        </model>
    </sbml>
    """


def test_sbml_endpoint_returns_visualization_scene(
    client: TestClient,
    sbml_document: bytes,
) -> None:
    response = client.post(
        "/api/v1/pathways/import/sbml",
        content=sbml_document,
        headers={"Content-Type": "application/sbml+xml"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["pathway_identity"]
    assert len(data["nodes"]) == 3
    assert len(data["edges"]) == 2
    assert data["bounds"] is not None


def test_sbml_endpoint_returns_metabolite_and_reaction_nodes(
    client: TestClient,
    sbml_document: bytes,
) -> None:
    response = client.post(
        "/api/v1/pathways/import/sbml",
        content=sbml_document,
        headers={"Content-Type": "application/xml"},
    )

    assert response.status_code == 200

    nodes = response.json()["nodes"]

    metabolite_nodes = [
        node for node in nodes
        if node["node_type"] == "metabolite"
    ]

    reaction_nodes = [
        node for node in nodes
        if node["node_type"] == "reaction"
    ]

    assert len(metabolite_nodes) == 2
    assert len(reaction_nodes) == 1


def test_sbml_endpoint_preserves_stoichiometric_coefficients(
    client: TestClient,
    sbml_document: bytes,
) -> None:
    response = client.post(
        "/api/v1/pathways/import/sbml",
        content=sbml_document,
        headers={"Content-Type": "application/sbml+xml"},
    )

    assert response.status_code == 200

    coefficients = {
        Decimal(edge["coefficient"])
        for edge in response.json()["edges"]
    }

    assert coefficients == {
        Decimal(1),
        Decimal(2),
    }


def test_sbml_endpoint_supports_force_directed_layout(
    client: TestClient,
    sbml_document: bytes,
) -> None:
    response = client.post(
        "/api/v1/pathways/import/sbml",
        params={"layout_id": "force-directed"},
        content=sbml_document,
        headers={"Content-Type": "application/sbml+xml"},
    )

    assert response.status_code == 200
    assert len(response.json()["nodes"]) == 3


def test_sbml_endpoint_rejects_unknown_layout(
    client: TestClient,
    sbml_document: bytes,
) -> None:
    response = client.post(
        "/api/v1/pathways/import/sbml",
        params={"layout_id": "unknown-layout"},
        content=sbml_document,
        headers={"Content-Type": "application/sbml+xml"},
    )

    assert response.status_code == 400


def test_sbml_endpoint_rejects_invalid_xml(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/pathways/import/sbml",
        content=b"<invalid-xml>",
        headers={"Content-Type": "application/sbml+xml"},
    )

    assert response.status_code == 422


def test_sbml_endpoint_rejects_empty_body(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/pathways/import/sbml",
        content=b"",
        headers={"Content-Type": "application/sbml+xml"},
    )

    assert response.status_code == 422


def test_sbml_endpoint_rejects_unsupported_content_type(
    client: TestClient,
    sbml_document: bytes,
) -> None:
    response = client.post(
        "/api/v1/pathways/import/sbml",
        content=sbml_document,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 415


def test_sbml_endpoint_rejects_empty_layout_identifier(
    client: TestClient,
    sbml_document: bytes,
) -> None:
    response = client.post(
        "/api/v1/pathways/import/sbml",
        params={"layout_id": ""},
        content=sbml_document,
        headers={"Content-Type": "application/sbml+xml"},
    )

    assert response.status_code == 422