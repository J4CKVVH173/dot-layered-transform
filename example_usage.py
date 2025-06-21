"""
Пример использования парсера DOT файлов для анализа архитектуры.
"""

from dot_parser import parse_dot_file, EdgeType, NodeType
from typing import Dict, List, Set


class ArchitectureAnalyzer:
    """Анализатор архитектуры на основе графа зависимостей."""

    def __init__(self, graph):
        self.graph = graph

    def get_layer_modules(self, layer_name: str) -> List[str]:
        """Получить все модули определённого слоя."""
        return [
            node_id
            for node_id in self.graph.nodes.keys()
            if f"::{layer_name}" in node_id
        ]

    def get_dependencies(self, node_id: str) -> Dict[str, List[str]]:
        """Получить зависимости узла, разделённые по типам."""
        edges = self.graph.get_edges_from(node_id)
        dependencies = {"owns": [], "uses": []}

        for edge in edges:
            dep_type = edge.attributes.edge_type.value
            dependencies[dep_type].append(edge.target)

        return dependencies

    def find_circular_dependencies(self) -> List[List[str]]:
        """Найти циклические зависимости (простой алгоритм)."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node, path):
            if node in rec_stack:
                # Найден цикл
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.graph.get_neighbors(node):
                dfs(neighbor, path + [neighbor])

            rec_stack.remove(node)

        for node_id in self.graph.nodes:
            if node_id not in visited:
                dfs(node_id, [node_id])

        return cycles

    def get_layer_violations(self) -> List[Dict]:
        """Найти нарушения слоёв архитектуры."""
        violations = []
        layers = ["domain", "application", "infrastructure"]

        for i, layer in enumerate(layers):
            layer_modules = self.get_layer_modules(layer)

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

    def get_statistics(self) -> Dict:
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
            layer_modules = self.get_layer_modules(layer)
            stats["layers"][layer] = len(layer_modules)

        return stats


def main():
    """Основная функция демонстрации."""
    print("=== АНАЛИЗ АРХИТЕКТУРЫ EVENT_SOURCING ===\n")

    # Парсим граф
    graph = parse_dot_file("example/graph.dot")
    analyzer = ArchitectureAnalyzer(graph)

    # Общая статистика
    stats = analyzer.get_statistics()
    print("📊 ОБЩАЯ СТАТИСТИКА:")
    print(f"  Узлов: {stats['total_nodes']}")
    print(f"  Рёбер: {stats['total_edges']}")
    print(f"  Типы узлов: {stats['node_types']}")
    print(f"  Типы рёбер: {stats['edge_types']}")
    print(f"  Модули по слоям: {stats['layers']}")
    print()

    # Анализ зависимостей основных слоёв
    print("🏗️ АНАЛИЗ СЛОЁВ:")
    layers = ["application", "domain", "infrastructure"]
    for layer in layers:
        main_module = f"event_sourcing::{layer}"
        if main_module in graph.nodes:
            deps = analyzer.get_dependencies(main_module)
            print(f"  {layer.upper()}:")
            print(f"    Владеет: {len(deps['owns'])} модулями")
            print(f"    Использует: {len(deps['uses'])} модулей")
            if deps["uses"]:
                print(
                    f"    Зависимости: {deps['uses'][:3]}{'...' if len(deps['uses']) > 3 else ''}"
                )
    print()

    # Поиск нарушений архитектуры
    print("⚠️ НАРУШЕНИЯ АРХИТЕКТУРЫ:")
    violations = analyzer.get_layer_violations()
    if violations:
        for violation in violations[:5]:  # Показываем первые 5
            print(f"  {violation['source_layer']} -> {violation['target_layer']}")
            print(f"    {violation['source']} использует {violation['target']}")
    else:
        print("  Нарушений не найдено!")
    print()

    # Поиск циклических зависимостей
    print("🔄 ЦИКЛИЧЕСКИЕ ЗАВИСИМОСТИ:")
    cycles = analyzer.find_circular_dependencies()
    if cycles:
        print(f"  Найдено циклов: {len(cycles)}")
        for i, cycle in enumerate(cycles[:3]):  # Показываем первые 3
            print(f"  Цикл {i+1}: {' -> '.join(cycle)}")
    else:
        print("  Циклических зависимостей не найдено!")
    print()

    print("✅ Анализ завершён!")


if __name__ == "__main__":
    main()
