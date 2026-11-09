
import pytest

from aditi.domain.entities.identifiers import ExternalIdentifier


def test_create_external_identifier():
    identifier = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
    )

    assert identifier.namespace == "UniProt"
    assert identifier.value == "P04637"
    assert identifier.url is None


def test_create_external_identifier_with_url():
    identifier = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
        url="https://www.uniprot.org/uniprotkb/P04637",
    )

    assert identifier.url == "https://www.uniprot.org/uniprotkb/P04637"


def test_qualified_value():
    identifier = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
    )

    assert identifier.qualified_value == "UniProt:P04637"


@pytest.mark.parametrize(
    "namespace",
    [
        "",
        " ",
        " UniProt",
        "UniProt ",
        None,
        123,
    ],
)
def test_reject_invalid_namespace(namespace):
    with pytest.raises(ValueError, match="namespace"):
        ExternalIdentifier(
            namespace=namespace,
            value="P04637",
        )


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        " P04637",
        "P04637 ",
        None,
        123,
    ],
)
def test_reject_invalid_identifier_value(value):
    with pytest.raises(ValueError, match="value"):
        ExternalIdentifier(
            namespace="UniProt",
            value=value,
        )


@pytest.mark.parametrize(
    "url",
    [
        "",
        " ",
        "ftp://example.com/resource",
        "not-a-url",
        "https://",
        123,
    ],
)
def test_reject_invalid_url(url):
    with pytest.raises(ValueError, match="URL"):
        ExternalIdentifier(
            namespace="UniProt",
            value="P04637",
            url=url,
        )


def test_external_identifier_is_immutable():
    identifier = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
    )

    with pytest.raises(AttributeError):
        identifier.value = "P12345"


def test_external_identifiers_are_hashable():
    first = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
    )

    second = ExternalIdentifier(
        namespace="PDB",
        value="1TUP",
    )

    identifiers = {first, second}

    assert len(identifiers) == 2


def test_external_identifier_equality():
    first = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
    )

    second = ExternalIdentifier(
        namespace="UniProt",
        value="P04637",
    )

    assert first == second


def test_different_namespaces_produce_different_identifiers():
    first = ExternalIdentifier(
        namespace="UniProt",
        value="12345",
    )

    second = ExternalIdentifier(
        namespace="PDB",
        value="12345",
    )

    assert first != second
