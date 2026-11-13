
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from aditi.api.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def make_alignment_request(
    first: str = "ACGT",
    second: str = "AGT",
    *,
    alphabet: str = "dna",
    alignment_type: str = "global",
    scoring: dict | None = None,
    gap: dict | None = None,
) -> dict:
    """Build a valid pairwise alignment API request."""

    return {
        "first_sequence": {
            "name": "First sequence",
            "residues": first,
            "alphabet": alphabet,
        },
        "second_sequence": {
            "name": "Second sequence",
            "residues": second,
            "alphabet": alphabet,
        },
        "alignment_type": alignment_type,
        "scoring": scoring or {
            "method": "simple",
            "match_score": 2.0,
            "mismatch_score": -1.0,
        },
        "gap": gap or {
            "model": "linear",
            "gap_penalty": -2.0,
        },
    }


def test_pairwise_endpoint_returns_global_dna_alignment(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/alignments/pairwise",
        json=make_alignment_request(),
    )

    assert response.status_code == 200

    result = response.json()

    assert result["alignment_type"] == "global"
    assert result["sequence_count"] == 2
    assert result["alignment_length"] >= 4
    assert len(result["aligned_sequences"]) == 2

    first, second = result["aligned_sequences"]

    assert first["sequence_name"] == "First sequence"
    assert second["sequence_name"] == "Second sequence"

    assert len(first["residues"]) == result["alignment_length"]
    assert len(second["residues"]) == result["alignment_length"]

    assert len(first["position_mapping"]) == result["alignment_length"]
    assert len(second["position_mapping"]) == result["alignment_length"]

    assert result["score"]["scoring_scheme"]


def test_pairwise_endpoint_returns_local_alignment_with_position_mapping(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/alignments/pairwise",
        json=make_alignment_request(
            first="TTACGTAA",
            second="GGACGTCC",
            alignment_type="local",
        ),
    )

    assert response.status_code == 200

    result = response.json()

    assert result["alignment_type"] == "local"
    assert result["sequence_count"] == 2

    first, second = result["aligned_sequences"]

    assert first["residues"].replace("-", "") == "ACGT"
    assert second["residues"].replace("-", "") == "ACGT"

    assert any(
        position is not None and position > 0
        for position in first["position_mapping"]
    )


def test_pairwise_endpoint_supports_affine_gap_penalties(
    client: TestClient,
) -> None:
    request = make_alignment_request(
        first="ACGT",
        second="AGT",
        gap={
            "model": "affine",
            "gap_open_penalty": -5.0,
            "gap_extension_penalty": -1.0,
        },
    )

    response = client.post(
        "/api/v1/alignments/pairwise",
        json=request,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["score"]["gap_open_penalty"] == -5.0
    assert result["score"]["gap_extension_penalty"] == -1.0


def test_pairwise_endpoint_supports_blosum62_protein_alignment(
    client: TestClient,
) -> None:
    request = make_alignment_request(
        first="MKWVTF",
        second="MKWYTF",
        alphabet="protein",
        scoring={
            "method": "substitution_matrix",
            "matrix_name": "BLOSUM62",
        },
    )

    response = client.post(
        "/api/v1/alignments/pairwise",
        json=request,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["alignment_type"] == "global"
    assert result["score"]["substitution_matrix"] == "BLOSUM62"
    assert result["sequence_count"] == 2


def test_pairwise_endpoint_rejects_invalid_dna_residue(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/alignments/pairwise",
        json=make_alignment_request(first="ACGX"),
    )

    assert response.status_code == 422


def test_pairwise_endpoint_rejects_mismatched_alphabets(
    client: TestClient,
) -> None:
    request = make_alignment_request()

    request["second_sequence"]["alphabet"] = "rna"

    response = client.post(
        "/api/v1/alignments/pairwise",
        json=request,
    )

    assert response.status_code == 422


def test_pairwise_endpoint_rejects_blosum62_for_dna(
    client: TestClient,
) -> None:
    request = make_alignment_request(
        scoring={
            "method": "substitution_matrix",
            "matrix_name": "BLOSUM62",
        },
    )

    response = client.post(
        "/api/v1/alignments/pairwise",
        json=request,
    )

    assert response.status_code == 422


def test_pairwise_endpoint_rejects_multiple_alignment(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/alignments/pairwise",
        json=make_alignment_request(alignment_type="multiple"),
    )

    assert response.status_code == 422


def test_pairwise_endpoint_rejects_invalid_payload(
    client: TestClient,
) -> None:
    request = make_alignment_request()
    del request["second_sequence"]

    response = client.post(
        "/api/v1/alignments/pairwise",
        json=request,
    )

    assert response.status_code == 422


def test_openapi_schema_includes_pairwise_alignment_endpoint(
    client: TestClient,
) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert "/api/v1/alignments/pairwise" in schema["paths"]
    assert "post" in schema["paths"]["/api/v1/alignments/pairwise"]
