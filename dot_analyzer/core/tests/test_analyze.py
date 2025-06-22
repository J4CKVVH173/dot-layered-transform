from dot_analyzer.core.tests.fixtures.circled_nodes import CIRCLED_NODES
from dot_analyzer.core.analyzer import ArchitectureAnalyzer, LayerViolation


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
            "unknown": 0,
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


def test_domain_to_domain_no_violation(parser, domain_to_domain_dot_content):
    graph = parser.parse_content(domain_to_domain_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    assert result == []


def test_application_to_application_no_violation(parser, application_to_application_dot_content):
    graph = parser.parse_content(application_to_application_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    assert result == []


def test_infrastructure_to_infrastructure_no_violation(parser, infrastructure_to_infrastructure_dot_content):
    graph = parser.parse_content(infrastructure_to_infrastructure_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    assert result == []


def test_application_uses_domain_no_violation(parser, application_uses_domain_dot_content):
    graph = parser.parse_content(application_uses_domain_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    assert result == []


def test_infrastructure_uses_application_no_violation(parser, infrastructure_uses_application_dot_content):
    graph = parser.parse_content(infrastructure_uses_application_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    assert result == []


def test_infrastructure_uses_domain_violation(parser, infrastructure_uses_domain_dot_content):
    graph = parser.parse_content(infrastructure_uses_domain_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    expected_violations = [
        LayerViolation(
            source="my_app::infrastructure::module_a",
            target="my_app::domain::module_b",
            source_layer="infrastructure",
            target_layer="domain",
            violation_type="layer_dependency",
        ),
    ]
    assert result == expected_violations


def test_domain_uses_unknown_violation(parser, domain_uses_unknown_dot_content):
    graph = parser.parse_content(domain_uses_unknown_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    expected_violations = [
        LayerViolation(
            source="my_app::domain::module_a",
            target="my_app::unknown_module",
            source_layer="domain",
            target_layer="unknown",
            violation_type="layer_dependency",
        ),
    ]
    assert result == expected_violations


def test_application_uses_unknown_violation(parser, application_uses_unknown_dot_content):
    graph = parser.parse_content(application_uses_unknown_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    expected_violations = [
        LayerViolation(
            source="my_app::application::module_a",
            target="my_app::unknown_module",
            source_layer="application",
            target_layer="unknown",
            violation_type="layer_dependency",
        ),
    ]
    assert result == expected_violations


def test_infrastructure_uses_unknown_violation(parser, infrastructure_uses_unknown_dot_content):
    graph = parser.parse_content(infrastructure_uses_unknown_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    expected_violations = [
        LayerViolation(
            source="my_app::infrastructure::module_a",
            target="my_app::unknown_module",
            source_layer="infrastructure",
            target_layer="unknown",
            violation_type="layer_dependency",
        ),
    ]
    assert result == expected_violations


def test_domain_uses_no_layer_violation(parser, domain_uses_no_layer_dot_content):
    graph = parser.parse_content(domain_uses_no_layer_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    expected_violations = [
        LayerViolation(
            source="my_app::domain::module_a",
            target="my_app::no_layer_module",
            source_layer="domain",
            target_layer="unknown",  # Модуль без слоя будет отнесен к 'unknown'
            violation_type="layer_dependency",
        ),
    ]
    assert result == expected_violations


def test_application_uses_no_layer_violation(parser, application_uses_no_layer_dot_content):
    graph = parser.parse_content(application_uses_no_layer_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    expected_violations = [
        LayerViolation(
            source="my_app::application::module_a",
            target="my_app::no_layer_module",
            source_layer="application",
            target_layer="unknown",
            violation_type="layer_dependency",
        ),
    ]
    assert result == expected_violations


def test_application_uses_infrastructure_violation(parser, application_uses_infrastructure_dot_content):
    graph = parser.parse_content(application_uses_infrastructure_dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    result = analyzer.get_layer_violations()

    expected_violations = [
        LayerViolation(
            source="my_app::application::module_a",
            target="my_app::infrastructure::module_b",
            source_layer="application",
            target_layer="infrastructure",
            violation_type="layer_dependency",
        ),
    ]
    assert result == expected_violations
