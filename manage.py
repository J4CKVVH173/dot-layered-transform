import argparse
import sys

from dot_analyzer.core.dot_parser import DotParser
from dot_analyzer.core.analyzer import ArchitectureAnalyzer
from dot_analyzer.view.dot_builder import DotView


def main():
    parser = argparse.ArgumentParser(
        description="Process a DOT file and generate a layered DOT diagram."
    )
    parser.add_argument("input_dot_file", help="Path to the input DOT file.")
    parser.add_argument(
        "-o", "--output", help="Path to the output DOT file (default: stdout)."
    )

    args = parser.parse_args()

    try:
        with open(args.input_dot_file, "r") as f:
            dot_content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_dot_file}' not found.", file=sys.stderr)
        sys.exit(1)

    dot_parser = DotParser()
    graph = dot_parser.parse_content(dot_content)

    analyzer = ArchitectureAnalyzer(
        graph
    )  # ArchitectureAnalyzer is needed for LayerHierarchy
    visualizer = DotView()

    layered_dot_content = visualizer.to_layered_dot(graph, analyzer)

    if args.output:
        with open(args.output, "w") as f:
            f.write(layered_dot_content)
        print(f"Layered DOT diagram successfully written to '{args.output}'")
    else:
        print(layered_dot_content)


if __name__ == "__main__":
    main()
