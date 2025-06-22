from dataclasses import dataclass
from enum import Enum

from .dot_parser import EdgeType, Graph, Node


class Layer(Enum):
    DOMAIN = "domain"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    UNKNOWN = "unknown"


class LayerHierarchy:
    """Manages the hierarchy and order of architectural layers."""

    def __init__(self):
        self._layers = [
            Layer.DOMAIN,
            Layer.APPLICATION,
            Layer.INFRASTRUCTURE,
            Layer.UNKNOWN,
        ]
        self._layer_to_index = {layer: i for i, layer in enumerate(self._layers)}

    def get_layer_index(self, layer: Layer) -> int:
        """Get the index of a given layer."""
        return self._layer_to_index[layer]

    def get_layer_by_name(self, name: str) -> Layer | None:
        """Get a Layer enum member by its string name."""
        for layer in self._layers:
            if layer.value == name:
                return layer
        return None

    def is_higher_layer(self, layer1: Layer, layer2: Layer) -> bool:
        """Check if layer1 is a higher layer than layer2."""
        return self.get_layer_index(layer1) > self.get_layer_index(layer2)

    def get_all_layer_names(self) -> list[str]:
        """Get a list of all layer names."""
        return [layer.value for layer in self._layers]


@dataclass
class LayerViolation:
    """Represents a violation of architectural layer dependencies."""

    source: str
    target: str
    source_layer: str
    target_layer: str
    violation_type: str = "layer_dependency"


class ArchitectureAnalyzer:
    """Architecture analyzer based on the dependency graph."""

    __slots__ = ("graph",)

    def __init__(self, graph: Graph):
        self.graph = graph

    def find_circular_dependencies(self) -> list[list[Node]]:
        """Find circular dependencies (simple algorithm)."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: Node, path):
            if node in rec_stack:
                # Cycle found
                cycle_start_index = path.index(node)
                cycle = path[cycle_start_index:]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)

            for edge in self.graph.get_edges_from(node.id):
                if edge.attributes.edge_type == EdgeType.USES:
                    neighbor_node = self.graph.get_node(edge.target)
                    if neighbor_node:
                        dfs(neighbor_node, path + [neighbor_node])

            rec_stack.remove(node)

        for node_id, node in self.graph.nodes.items():
            if node not in visited:
                dfs(node, [node])

        return cycles

    def get_dependencies(self, node_id: str) -> dict[str, list[str]]:
        """Get node dependencies, separated by type."""
        edges = self.graph.get_edges_from(node_id)
        dependencies = {"owns": [], "uses": []}

        for edge in edges:
            dep_type = edge.attributes.edge_type.value
            dependencies[dep_type].append(edge.target)

        return dependencies

    def get_layer_violations(self) -> list[LayerViolation]:
        """Find architectural layer violations."""
        violations = []
        layer_hierarchy = LayerHierarchy()
        layers = layer_hierarchy.get_all_layer_names()

        for i, layer in enumerate(layers):
            layer_modules = self._get_layer_modules(layer)

            for module_id in layer_modules:
                module_node = self.graph.get_node(module_id)
                if module_node and module_node.attributes.node_type.value == "crate":
                    continue  # Skip crate nodes

                edges = self.graph.get_edges_from(module_id)
                uses_edges = [
                    e for e in edges if e.attributes.edge_type == EdgeType.USES
                ]

                for edge in uses_edges:
                    source_layer_enum = layer_hierarchy.get_layer_by_name(layer)

                    target_layer_enum = Layer.UNKNOWN  # Default to UNKNOWN if no layer found
                    for target_layer_name in layers:
                        if f"::{target_layer_name}" in edge.target:
                            target_layer_enum = layer_hierarchy.get_layer_by_name(
                                target_layer_name
                            )
                            break

                    # Check for violation: a layer should not depend on layers above it
                    if source_layer_enum == Layer.DOMAIN:
                        # Domain can only depend on Domain
                        if target_layer_enum and target_layer_enum != Layer.DOMAIN:
                            violations.append(
                                LayerViolation(
                                    source=module_id,
                                    target=edge.target,
                                    source_layer=source_layer_enum.value,
                                    target_layer=target_layer_enum.value,
                                )
                            )
                    elif source_layer_enum == Layer.APPLICATION:
                        # Application can only depend on Domain or Application
                        if target_layer_enum and target_layer_enum not in [
                            Layer.DOMAIN,
                            Layer.APPLICATION,
                        ]:
                            violations.append(
                                LayerViolation(
                                    source=module_id,
                                    target=edge.target,
                                    source_layer=source_layer_enum.value,
                                    target_layer=target_layer_enum.value,
                                )
                            )
                    elif source_layer_enum == Layer.INFRASTRUCTURE:
                        # Infrastructure can only depend on Application or Infrastructure
                        if target_layer_enum and target_layer_enum not in [
                            Layer.APPLICATION,
                            Layer.INFRASTRUCTURE,
                        ]:
                            violations.append(
                                LayerViolation(
                                    source=module_id,
                                    target=edge.target,
                                    source_layer=source_layer_enum.value,
                                    target_layer=target_layer_enum.value,
                                )
                            )
                    elif source_layer_enum == Layer.UNKNOWN:
                        # UNKNOWN layer can depend on anything, no violations here
                        pass

        return violations

    def _get_layer_modules(self, layer_name: str) -> list[str]:
        """Get all modules of a specific layer."""
        return [
            node_id
            for node_id in self.graph.nodes.keys()
            if f"::{layer_name}" in node_id
        ]

    def get_statistics(self) -> dict:
        """Get graph statistics."""
        stats = {
            "total_nodes": len(self.graph.nodes),
            "total_edges": len(self.graph.edges),
            "node_types": {},
            "edge_types": {},
            "layers": {},
        }

        # Node statistics
        for node in self.graph.nodes.values():
            node_type = node.attributes.node_type.value
            stats["node_types"][node_type] = stats["node_types"].get(node_type, 0) + 1

        # Edge statistics
        for edge in self.graph.edges:
            edge_type = edge.attributes.edge_type.value
            stats["edge_types"][edge_type] = stats["edge_types"].get(edge_type, 0) + 1

        # Layer statistics
        layer_hierarchy = LayerHierarchy()
        layers = layer_hierarchy.get_all_layer_names()
        for layer in layers:
            layer_modules = self._get_layer_modules(layer)
            stats["layers"][layer] = len(layer_modules)

        return stats
