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
