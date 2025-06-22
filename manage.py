import argparse
import sys

from dot_analyzer.core.dot_parser import DotParser
from dot_analyzer.core.analyzer import ArchitectureAnalyzer
from dot_analyzer.view.dot_builder import DotView


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and transform DOT files for architectural layer visualization.",
        prog="dot-layered-transform"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Transform command (existing functionality)
    transform_parser = subparsers.add_parser(
        "transform",
        help="Transform DOT file to layered visualization"
    )
    transform_parser.add_argument("input_dot_file", help="Path to the input DOT file.")
    transform_parser.add_argument(
        "-o", "--output", help="Path to the output DOT file (default: stdout)."
    )
    
    # Analyze command (new functionality)
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze DOT file for architectural violations and cycles"
    )
    analyze_parser.add_argument("input_dot_file", help="Path to the input DOT file.")
    analyze_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Load and parse DOT file
    try:
        with open(args.input_dot_file, "r") as f:
            dot_content = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_dot_file}' not found.", file=sys.stderr)
        sys.exit(1)

    dot_parser = DotParser()
    graph = dot_parser.parse_content(dot_content)
    analyzer = ArchitectureAnalyzer(graph)

    if args.command == "transform":
        _handle_transform(graph, analyzer, args)
    elif args.command == "analyze":
        _handle_analyze(analyzer, args)


def _handle_transform(graph, analyzer, args):
    """Handle transform command."""
    visualizer = DotView()
    layered_dot_content = visualizer.to_layered_dot(graph, analyzer)

    if args.output:
        with open(args.output, "w") as f:
            f.write(layered_dot_content)
        print(f"Layered DOT diagram successfully written to '{args.output}'")
    else:
        print(layered_dot_content)


def _handle_analyze(analyzer, args):
    """Handle analyze command."""
    violations = analyzer.get_layer_violations()
    cycles = analyzer.find_circular_dependencies()
    
    if args.format == "json":
        import json
        result = {
            "violations": [
                {
                    "source": v.source,
                    "target": v.target,
                    "source_layer": v.source_layer,
                    "target_layer": v.target_layer,
                    "type": v.violation_type
                }
                for v in violations
            ],
            "circular_dependencies": [
                [node.id for node in cycle]
                for cycle in cycles
            ]
        }
        print(json.dumps(result, indent=2))
    else:
        print("=== Architecture Analysis ===\n")
        
        if violations:
            print(f"Found {len(violations)} layer violations:")
            for i, violation in enumerate(violations, 1):
                print(f"  {i}. {violation.source} -> {violation.target}")
                print(f"     ({violation.source_layer} -> {violation.target_layer})")
        else:
            print("✓ No layer violations found")
        
        print()
        
        if cycles:
            print(f"Found {len(cycles)} circular dependencies:")
            for i, cycle in enumerate(cycles, 1):
                cycle_str = " -> ".join([node.id for node in cycle])
                print(f"  {i}. {cycle_str}")
        else:
            print("✓ No circular dependencies found")


if __name__ == "__main__":
    main()
