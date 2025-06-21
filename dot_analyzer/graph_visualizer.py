from .dot_parser import Graph
from analyzer import ArchitectureAnalyzer, LayerHierarchy


class GraphVisualizer:
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

        # Define colors for layers and nodes
        layer_colors = {
            "domain": "#ADD8E6",
            "application": "#90EE90",
            "infrastructure": "#FFD700",
            "root": "#D3D3D3",
        }
        node_fill_color = "#FFFFFF"  # White for all nodes

        layer_hierarchy = LayerHierarchy()
        layers = layer_hierarchy.get_all_layer_names()

        # Group nodes by layer
        nodes_by_layer = {layer: [] for layer in layers}
        # Add a 'root' category for nodes not explicitly in a defined layer
        nodes_by_layer["root"] = []

        for node_id, node in graph.nodes.items():
            assigned_to_layer = False
            for layer_name in layers:
                if f"::{layer_name}" in node_id:
                    nodes_by_layer[layer_name].append(node)
                    assigned_to_layer = True
                    break
            if not assigned_to_layer:
                nodes_by_layer["root"].append(node)

        # Add subgraphs for each layer
        for layer_name in layers:
            if nodes_by_layer[layer_name]:
                dot_lines.append(f"    subgraph cluster_{layer_name} {{")
                dot_lines.append(f'        label="{layer_name.capitalize()} Layer";')
                dot_lines.append("        style=filled;")
                dot_lines.append(f"        color=\"{layer_colors.get(layer_name, '#D3D3D3')}\";")
                dot_lines.append(f"        node [fillcolor=\"{node_fill_color}\"];")
                for node in nodes_by_layer[layer_name]:
                    dot_lines.append(
                        f'        "{node.id}" [label="{node.attributes.label}"];'
                    )
                dot_lines.append("    }")

        # Add root node if exists and not part of a layer subgraph
        if nodes_by_layer["root"]:
            dot_lines.append(f"    subgraph cluster_root {{")  # noqa
            dot_lines.append(f"        label=\"Other Nodes\";")  # noqa
            dot_lines.append("        style=filled;")
            dot_lines.append(f"        color=\"{layer_colors.get('root', '#D3D3D3')}\";")
            dot_lines.append(f"        node [fillcolor=\"{node_fill_color}\"];")
            for node in nodes_by_layer["root"]:
                dot_lines.append(f'        "{node.id}" [label="{node.attributes.label}"];')
            dot_lines.append("    }")

        # Add edges
        for edge in graph.edges:
            edge_color = "black"
            if edge.attributes.edge_type.value == "uses":
                edge_color = "blue"
            elif edge.attributes.edge_type.value == "owns":
                edge_color = "darkgreen"

            dot_lines.append(
                f'    "{edge.source}" -> "{edge.target}" [label="{edge.attributes.edge_type.value}", color="{edge_color}"];'  # noqa
            )

        dot_lines.append("}")
        return "\n".join(dot_lines)
