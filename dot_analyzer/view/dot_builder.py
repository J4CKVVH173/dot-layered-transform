from dot_analyzer.core.dot_parser import Graph
from dot_analyzer.core.analyzer import ArchitectureAnalyzer, LayerHierarchy


class DotView:
    """
    A class to visualize architectural graphs, specifically for generating
    DOT diagrams with modules grouped by layers.
    """

    def to_layered_dot(self, graph: Graph, analyzer: ArchitectureAnalyzer) -> str:
        """
        Converts the graph into a DOT diagram with visual grouping by layers.
        Modules are grouped into subgraphs based on their architectural layer.
        """
        dot_lines = []
        dot_lines.append("digraph G {")
        dot_lines.append("    rankdir=LR;")
        dot_lines.append("    node [shape=box, style=filled];")

        # Get violations and cycles from the analyzer
        layer_violations = analyzer.get_layer_violations()
        circular_dependencies = analyzer.find_circular_dependencies()

        total_violations = len(layer_violations) + len(circular_dependencies)
        if total_violations > 0:
            label_text = (
                f"Violations detected: Cycles: {len(circular_dependencies)}, Layer violations: {len(layer_violations)}"
            )
            dot_lines.append(f'    label="{label_text}";')
            dot_lines.append('    labelloc="b";')
            dot_lines.append('    labeljust="l";')
            dot_lines.append('    fontname="Helvetica";')
            dot_lines.append('    fontsize="10";')

        # Define colors for layers and nodes
        layer_colors = {
            "domain": "#A6C8FF",
            "application": "#9EEBB3",
            "infrastructure": "#FFE29A",
            "unknown": "#D3D3D3",
        }
        node_fill_color = "#FFFFFF"  # White for all nodes

        layer_hierarchy = LayerHierarchy()
        layers = layer_hierarchy.get_all_layer_names()

        # Group nodes by layer
        nodes_by_layer = {layer: [] for layer in layers}
        # Add an 'unknown' category for nodes not explicitly in a defined layer
        nodes_by_layer["unknown"] = []
        crate_nodes = []

        for node_id, node in graph.nodes.items():
            if node.attributes.node_type.value == "crate":
                crate_nodes.append(node)
                continue

            assigned_to_layer = False
            for layer_name in layers:
                if f"::{layer_name}" in node_id:
                    nodes_by_layer[layer_name].append(node)
                    assigned_to_layer = True
                    break
            if not assigned_to_layer:
                nodes_by_layer["unknown"].append(node)

        # Add subgraphs for each layer
        for layer_name in layers:
            if nodes_by_layer[layer_name]:
                dot_lines.append(f"    subgraph cluster_{layer_name} {{")
                dot_lines.append(f'        label="{layer_name.capitalize()} Layer";')
                dot_lines.append("        style=filled;")
                dot_lines.append(
                    f"        color=\"{layer_colors.get(layer_name, '#D3D3D3')}\";"
                )
                dot_lines.append(f'        node [fillcolor="{node_fill_color}"];')
                for node in nodes_by_layer[layer_name]:
                    dot_lines.append(
                        f'        "{node.id}" [label="{node.attributes.label}"];'
                    )
                dot_lines.append("    }")

            # Add crate nodes directly (not in a subgraph)
            for node in crate_nodes:
                dot_lines.append(
                    f'    "{node.id}" [label="{node.attributes.label}", shape=box, style=filled, fillcolor="#ADD8E6"];'
                )

        # Add unknown node if exists and not part of a layer subgraph
        if nodes_by_layer["unknown"]:
            dot_lines.append(f"    subgraph cluster_unknown {{")  # noqa
            dot_lines.append(f'        label="Unknown Layer";')  # noqa
            dot_lines.append("        style=filled;")
            dot_lines.append(
                f"        color=\"{layer_colors.get('unknown', '#D3D3D3')}\";"
            )
            dot_lines.append(f'        node [fillcolor="{node_fill_color}"];')
            for node in nodes_by_layer["unknown"]:
                dot_lines.append(
                    f'        "{node.id}" [label="{node.attributes.label}"];'
                )
            dot_lines.append("    }")

        # Convert circular dependencies to a set of (source, target) tuples for easy lookup
        circular_edges = set()
        for cycle in circular_dependencies:
            for i in range(len(cycle)):
                source_node = cycle[i]
                target_node = cycle[(i + 1) % len(cycle)]
                # Find the actual edge in the graph
                for edge in graph.edges:
                    if edge.source == source_node.id and edge.target == target_node.id:
                        circular_edges.add((edge.source, edge.target))
                        break

        # Add edges
        for edge in graph.edges:
            if edge.attributes.edge_type.value == "owns":
                edge_color = "black"
                dot_lines.append(
                    f'    "{edge.source}" -> "{edge.target}" '
                    f'[label="{edge.attributes.edge_type.value}", color="{edge_color}"];'
                )
            elif edge.attributes.edge_type.value == "uses":
                is_violation = False
                for violation in layer_violations:
                    if (
                        violation.source == edge.source
                        and violation.target == edge.target
                    ):
                        is_violation = True
                        break

                is_circular = (edge.source, edge.target) in circular_edges

                if is_violation or is_circular:
                    edge_color = "#f55c7a"  # Color for violations/cycles
                    dot_lines.append(
                        f'    "{edge.source}" -> "{edge.target}" '
                        f'[label="{edge.attributes.edge_type.value}", color="{edge_color}", style="dashed"];'
                    )

        dot_lines.append("}")
        return "\n".join(dot_lines)
