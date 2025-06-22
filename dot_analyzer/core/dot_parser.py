"""
DOT file parser for converting to Python graph data structures.
"""

from dataclasses import dataclass, field
from enum import Enum
import re


class EdgeType(Enum):
    """Edge types in the graph."""

    OWNS = "owns"
    USES = "uses"


class NodeType(Enum):
    """Node types in the graph."""

    CRATE = "crate"
    MODULE = "mod"


@dataclass
class GraphAttributes:
    """Graph attributes."""

    label: str
    labelloc: str = "t"
    pad: float = 0.4
    layout: str = "dot"
    overlap: bool = False
    splines: str = "line"
    rankdir: str = "LR"
    fontname: str = "Helvetica"
    fontsize: str = "36"


@dataclass
class NodeAttributes:
    """Node attributes."""

    label: str
    fillcolor: str
    node_type: NodeType
    visibility: str  # pub, pub(crate), pub(self)
    name: str


@dataclass
class EdgeAttributes:
    """Edge attributes."""

    label: str
    color: str
    style: str  # solid, dashed
    constraint: bool
    edge_type: EdgeType


@dataclass(eq=True, frozen=True)
class Node:
    """Graph node."""

    id: str
    attributes: NodeAttributes = field(compare=False, hash=False)


@dataclass
class Edge:
    """Graph edge."""

    source: str
    target: str
    attributes: EdgeAttributes


@dataclass
class Graph:
    """Graph representation."""

    attributes: GraphAttributes
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)

    def add_node(self, node: Node) -> None:
        """Add node to the graph."""
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        """Add edge to the graph."""
        self.edges.append(edge)

    def get_node(self, node_id: str) -> Node | None:
        """Get node by ID."""
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> list[str]:
        """Get node neighbors."""
        neighbors = []
        for edge in self.edges:
            if edge.source == node_id:
                neighbors.append(edge.target)
        return neighbors

    def get_edges_from(self, node_id: str) -> list[Edge]:
        """Get all edges outgoing from the node."""
        return [edge for edge in self.edges if edge.source == node_id]

    def get_edges_to(self, node_id: str) -> list[Edge]:
        """Get all edges incoming to the node."""
        return [edge for edge in self.edges if edge.target == node_id]


class DotParser:
    """DOT file parser."""

    def __init__(self):
        # Regular expressions for parsing
        self.node_pattern = re.compile(r'"([^"]+)"\s*\[([^\]]+)\];')
        self.edge_pattern = re.compile(
            r'"([^"]+)"\s*->\s*"([^"]+)"\s*\[([^\]]+)\](?:\s*\[([^\]]+)\])?\s*;'
        )
        self.graph_attr_pattern = re.compile(r"(\w+)=([^,\]]+)")

    def parse_attributes(self, attr_string: str) -> dict[str, str]:
        """Parse attribute string."""
        attributes = {}
        attr_string = attr_string.strip()

        # Split by commas, but consider quotes
        parts = []
        current_part = ""
        in_quotes = False

        for char in attr_string:
            if char == '"' and (not current_part or current_part[-1] != "\\"):
                in_quotes = not in_quotes
                current_part += char
            elif char == "," and not in_quotes:
                if current_part.strip():
                    parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char

        if current_part.strip():
            parts.append(current_part.strip())

        # Parse each part as key=value
        for part in parts:
            if "=" in part:
                key, value = part.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                attributes[key] = value

        return attributes

    def parse_node_label(self, label: str) -> tuple[NodeType, str, str]:
        """Parse node label to extract type, visibility and name."""
        # Format: "pub(crate) mod|application" or "crate|event_sourcing"
        if "|" in label:
            visibility_type, name = label.split("|", 1)
            if "crate" in visibility_type and "mod" not in visibility_type:
                return NodeType.CRATE, visibility_type.strip(), name.strip()
            else:
                return NodeType.MODULE, visibility_type.strip(), name.strip()
        else:
            return NodeType.MODULE, "unknown", label.strip()

    def parse_content(self, content: str) -> Graph:
        """Parse DOT file content."""
        lines = content.split("\n")

        # Initialize graph with basic attributes
        graph_attrs = GraphAttributes(label="")
        graph = Graph(attributes=graph_attrs)

        # Parse line by line
        in_graph_attrs = False

        for line in lines:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("//"):
                continue

            # Handle graph attributes
            if line.startswith("graph ["):
                in_graph_attrs = True
                continue
            elif in_graph_attrs and line == "];":
                in_graph_attrs = False
                continue
            elif in_graph_attrs:
                # Parse graph attributes
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().rstrip(",").strip('"').strip("'")

                    if key == "label":
                        graph.attributes.label = value
                    elif key == "layout":
                        graph.attributes.layout = value
                    elif key == "rankdir":
                        graph.attributes.rankdir = value
                    # Add other attributes as needed
                continue

            # Check edges first (they have priority)
            edge_match = self.edge_pattern.search(line)
            if edge_match:
                source = edge_match.group(1)
                target = edge_match.group(2)
                attr_string1 = edge_match.group(3)
                attr_string2 = edge_match.group(4) if edge_match.group(4) else ""

                # Combine attributes from both groups
                attrs = self.parse_attributes(attr_string1)
                if attr_string2:
                    attrs2 = self.parse_attributes(attr_string2)
                    attrs.update(attrs2)

                edge_type = (
                    EdgeType.OWNS if attrs.get("label") == "owns" else EdgeType.USES
                )
                edge_attrs = EdgeAttributes(
                    label=attrs.get("label", ""),
                    color=attrs.get("color", "#000000"),
                    style=attrs.get("style", "solid"),
                    constraint=attrs.get("constraint", "true").lower() == "true",
                    edge_type=edge_type,
                )
                edge = Edge(source=source, target=target, attributes=edge_attrs)
                graph.add_edge(edge)
                continue

            # Parse nodes (only if it's not an edge)
            node_match = self.node_pattern.search(line)
            if node_match and "->" not in line:
                node_id = node_match.group(1)
                attr_string = node_match.group(2)
                attrs = self.parse_attributes(attr_string)

                if "label" in attrs:
                    node_type, visibility, name = self.parse_node_label(attrs["label"])
                    node_attrs = NodeAttributes(
                        label=attrs["label"],
                        fillcolor=attrs.get("fillcolor", "#ffffff"),
                        node_type=node_type,
                        visibility=visibility,
                        name=name,
                    )
                    node = Node(id=node_id, attributes=node_attrs)
                    graph.add_node(node)
                continue

        return graph
