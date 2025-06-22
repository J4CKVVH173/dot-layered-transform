from os import path
from pathlib import Path
import pytest

CURRENT_DIR = Path(__file__).resolve().parent


@pytest.fixture
def simple_dot_content():
    with open(path.join(CURRENT_DIR, "simple.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def nested_dot_content():
    with open(path.join(CURRENT_DIR, "nested.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def circle_dot_content():
    with open(path.join(CURRENT_DIR, "circle.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def layered_dot_content():
    with open(path.join(CURRENT_DIR, "layered_graph.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def violated_layered_dot_content():
    with open(path.join(CURRENT_DIR, "violated_layered_graph.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def domain_to_domain_dot_content():
    with open(path.join(CURRENT_DIR, "domain_to_domain.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def application_to_application_dot_content():
    with open(path.join(CURRENT_DIR, "application_to_application.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def infrastructure_to_infrastructure_dot_content():
    with open(
        path.join(CURRENT_DIR, "infrastructure_to_infrastructure.dot"), "r"
    ) as diagram:
        return diagram.read()


@pytest.fixture
def application_uses_domain_dot_content():
    with open(path.join(CURRENT_DIR, "application_uses_domain.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def infrastructure_uses_application_dot_content():
    with open(
        path.join(CURRENT_DIR, "infrastructure_uses_application.dot"), "r"
    ) as diagram:
        return diagram.read()


@pytest.fixture
def infrastructure_uses_domain_dot_content():
    with open(path.join(CURRENT_DIR, "infrastructure_uses_domain.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def application_uses_infrastructure_dot_content():
    with open(
        path.join(CURRENT_DIR, "application_uses_infrastructure.dot"), "r"
    ) as diagram:
        return diagram.read()


@pytest.fixture
def domain_uses_unknown_dot_content():
    with open(path.join(CURRENT_DIR, "domain_uses_unknown.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def application_uses_unknown_dot_content():
    with open(path.join(CURRENT_DIR, "application_uses_unknown.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def infrastructure_uses_unknown_dot_content():
    with open(
        path.join(CURRENT_DIR, "infrastructure_uses_unknown.dot"), "r"
    ) as diagram:
        return diagram.read()


@pytest.fixture
def domain_uses_no_layer_dot_content():
    with open(path.join(CURRENT_DIR, "domain_uses_no_layer.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def application_uses_no_layer_dot_content():
    with open(path.join(CURRENT_DIR, "application_uses_no_layer.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def test_graph_input_content():
    with open(path.join(CURRENT_DIR, "complexes", "graph_input.dot"), "r") as diagram:
        return diagram.read()


@pytest.fixture
def test_graph_expected_content():
    with open(
        path.join(CURRENT_DIR, "complexes", "graph_expected.dot"), "r"
    ) as diagram:
        return diagram.read()
