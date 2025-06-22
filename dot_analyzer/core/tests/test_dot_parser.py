from .fixtures.simple_graph import simple_graph
from .fixtures.nested_graph import nested_graph
from .fixtures.circle_graph import circle_graph

from dot_analyzer.core.dot_parser import (
    DotParser,
    NodeType,
)


def test_parse_simple_dot_content(simple_dot_content, parser):
    """Тест парсинга простого DOT содержимого."""
    parsed_graph = parser.parse_content(simple_dot_content)

    expected = simple_graph()

    assert expected == parsed_graph


def test_parse_nested_dot_content(nested_dot_content, parser):
    """Тест парсинга простого DOT содержимого."""
    parsed_graph = parser.parse_content(nested_dot_content)

    expected = nested_graph()

    assert expected == parsed_graph


def test_parse_circle_dot_content(circle_dot_content, parser):
    """Тест парсинга простого DOT содержимого."""
    parsed_graph = parser.parse_content(circle_dot_content)

    expected = circle_graph()

    assert expected == parsed_graph


def test_graph_methods(simple_dot_content, parser):
    """Тест методов графа."""
    graph = parser.parse_content(simple_dot_content)

    # Тест get_neighbors
    neighbors = graph.get_neighbors("root")
    assert "root::module_a" in neighbors
    assert "root::module_b" in neighbors
    assert len(neighbors) == 2

    # Тест get_edges_from
    edges_from_root = graph.get_edges_from("root")
    assert len(edges_from_root) == 2
    assert all(edge.source == "root" for edge in edges_from_root)

    # Тест get_edges_to
    edges_to_module_b = graph.get_edges_to("root::module_b")
    assert len(edges_to_module_b) == 2  # от root и от module_a

    # Тест get_node
    root_node = graph.get_node("root")
    assert root_node is not None
    assert root_node.attributes.node_type == NodeType.CRATE

    non_existent = graph.get_node("non_existent")
    assert non_existent is None


def test_node_without_separator_type_parsing(parser):
    node_type, visibility, name = parser.parse_node_label("simple_label")

    assert node_type == NodeType.MODULE
    assert visibility == "unknown"
    assert name == "simple_label"


def test_create_node_type_parsing(parser):
    node_type, visibility, name = parser.parse_node_label("crate|test_crate")

    assert node_type == NodeType.CRATE
    assert visibility == "crate"
    assert name == "test_crate"


def test_module_type_parsing(parser):
    node_type, visibility, name = parser.parse_node_label("pub mod|test_module")

    assert node_type == NodeType.MODULE
    assert visibility == "pub mod"
    assert name == "test_module"


def test_attributes_parsing():
    """Test attr parsing."""
    parser = DotParser()

    attr_string = 'label="test", color="#ff0000", style="solid"'
    attrs = parser.parse_attributes(attr_string)

    assert attrs["label"] == "test"
    assert attrs["color"] == "#ff0000"
    assert attrs["style"] == "solid"
