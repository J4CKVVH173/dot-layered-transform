from dot_parser import EdgeType, Graph, Node


class ArchitectureAnalyzer:
    """Анализатор архитектуры на основе графа зависимостей."""

    __slots__ = ('graph',)

    def __init__(self, graph: Graph):
        self.graph = graph

    def find_circular_dependencies(self) -> list[list[Node]]:
        """Найти циклические зависимости (простой алгоритм)."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: Node, path):
            if node in rec_stack:
                # Найден цикл
                cycle_start_index = path.index(node)
                cycle = path[cycle_start_index:]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)

            for neighbor_id in self.graph.get_neighbors(node.id):
                neighbor_node = self.graph.get_node(neighbor_id)
                if neighbor_node:
                    dfs(neighbor_node, path + [neighbor_node])

            rec_stack.remove(node)

        for node_id, node in self.graph.nodes.items():
            if node not in visited:
                dfs(node, [node])

        return cycles

    def _get_layer_modules(self, layer_name: str) -> list[str]:
        """Получить все модули определённого слоя."""
        return [
            node_id
            for node_id in self.graph.nodes.keys()
            if f"::{layer_name}" in node_id
        ]

    def get_dependencies(self, node_id: str) -> dict[str, list[str]]:
        """Получить зависимости узла, разделённые по типам."""
        edges = self.graph.get_edges_from(node_id)
        dependencies = {"owns": [], "uses": []}

        for edge in edges:
            dep_type = edge.attributes.edge_type.value
            dependencies[dep_type].append(edge.target)

        return dependencies

    def get_layer_violations(self) -> list[dict]:
        """Найти нарушения слоёв архитектуры."""
        violations = []
        layers = ["domain", "application", "infrastructure"]

        for i, layer in enumerate(layers):
            layer_modules = self._get_layer_modules(layer)

            for module in layer_modules:
                edges = self.graph.get_edges_from(module)
                uses_edges = [
                    e for e in edges if e.attributes.edge_type == EdgeType.USES
                ]

                for edge in uses_edges:
                    target_layer = None
                    for j, target_layer_name in enumerate(layers):
                        if f"::{target_layer_name}" in edge.target:
                            target_layer = j
                            break

                    # Проверяем нарушение: слой не должен зависеть от слоёв выше
                    if target_layer is not None and target_layer > i:
                        violations.append(
                            {
                                "source": module,
                                "target": edge.target,
                                "source_layer": layer,
                                "target_layer": layers[target_layer],
                                "violation_type": "layer_dependency",
                            }
                        )

        return violations

    def get_statistics(self) -> dict:
        """Получить статистику по графу."""
        stats = {
            "total_nodes": len(self.graph.nodes),
            "total_edges": len(self.graph.edges),
            "node_types": {},
            "edge_types": {},
            "layers": {},
        }

        # Статистика узлов
        for node in self.graph.nodes.values():
            node_type = node.attributes.node_type.value
            stats["node_types"][node_type] = stats["node_types"].get(node_type, 0) + 1

        # Статистика рёбер
        for edge in self.graph.edges:
            edge_type = edge.attributes.edge_type.value
            stats["edge_types"][edge_type] = stats["edge_types"].get(edge_type, 0) + 1

        # Статистика слоёв
        layers = ["application", "domain", "infrastructure"]
        for layer in layers:
            layer_modules = self._get_layer_modules(layer)
            stats["layers"][layer] = len(layer_modules)

        return stats
