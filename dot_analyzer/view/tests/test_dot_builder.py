from dot_analyzer.core.analyzer import ArchitectureAnalyzer
from dot_analyzer.view.dot_builder import DotView
from dot_analyzer.core.dot_parser import DotParser


def test_to_layered_dot_output(test_graph_input_content, test_graph_expected_content):
    parser = DotParser()
    graph = parser.parse_content(test_graph_input_content)
    analyzer = ArchitectureAnalyzer(graph)
    dot_view = DotView()

    result = dot_view.to_layered_dot(graph, analyzer)

    assert result == test_graph_expected_content
