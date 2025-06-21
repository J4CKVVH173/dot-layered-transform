from dot_analyzer.tests.fixtures.circled_nodes import CIRCLED_NODES
from dot_analyzer.analyzer import ArchitectureAnalyzer, LayerViolation


def test_analyze_simple_to_have_circle(parser, simple_dot_content):
    graph = parser.parse_content(simple_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.find_circular_dependencies()

    assert result == []


def test_analyze_nested_to_have_circle(parser, nested_dot_content):
    graph = parser.parse_content(nested_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.find_circular_dependencies()

    assert result == []


def test_analyze_graph_with_circle(parser, circle_dot_content):
    graph = parser.parse_content(circle_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.find_circular_dependencies()

    assert result == CIRCLED_NODES, f"Ожидался {CIRCLED_NODES}, но получен {result}"


def test_analyze_statistics(parser, nested_dot_content):
    graph = parser.parse_content(nested_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_statistics()

    expected_statistics = {
        "edge_types": {
            "owns": 5,
            "uses": 2,
        },
        "layers": {
            "application": 0,
            "domain": 0,
            "infrastructure": 0,
        },
        "node_types": {
            "crate": 1,
            "mod": 5,
        },
        "total_edges": 7,
        "total_nodes": 6,
    }
    assert result == expected_statistics


def test_checks_violated_layered(parser, layered_dot_content):
    graph = parser.parse_content(layered_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    assert result == []


def test_checks_graph_with_violated_layers(parser, violated_layered_dot_content):
    graph = parser.parse_content(violated_layered_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    expected_violations = [
        LayerViolation(
            source="event_sourcing::domain::event",
            target="event_sourcing::infrastructure::input::cli",
            source_layer="domain",
            target_layer="infrastructure",
            violation_type="layer_dependency",
        ),
    ]
    assert result == expected_violations
