from tests.fixtures.circled_nodes import CIRCLED_NODES
from analyzer import ArchitectureAnalyzer


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
