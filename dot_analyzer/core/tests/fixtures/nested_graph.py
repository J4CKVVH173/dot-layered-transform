from dot_analyzer.core.dot_parser import (
    Graph,
    Node,
    Edge,
    NodeAttributes,
    EdgeAttributes,
    GraphAttributes,
    NodeType,
    EdgeType,
)


def nested_graph():
    """Function to get nested.dot as python object."""
    graph_attrs = GraphAttributes(label="test_graph", layout="dot", rankdir="LR")

    root_node = Node(
        id="root",
        attributes=NodeAttributes(
            label="crate|root",
            fillcolor="#5397c8",
            node_type=NodeType.CRATE,
            visibility="crate",
            name="root",
        ),
    )

    module_a_node = Node(
        id="root::module_a",
        attributes=NodeAttributes(
            label="pub mod|module_a",
            fillcolor="#81c169",
            node_type=NodeType.MODULE,
            visibility="pub mod",
            name="module_a",
        ),
    )

    module_b_node = Node(
        id="root::module_b",
        attributes=NodeAttributes(
            label="pub(crate) mod|module_b",
            fillcolor="#f8c04c",
            node_type=NodeType.MODULE,
            visibility="pub(crate) mod",
            name="module_b",
        ),
    )

    submodule_a1_node = Node(
        id="root::module_a::submodule_a1",
        attributes=NodeAttributes(
            label="pub mod|submodule_a1",
            fillcolor="#a5d987",
            node_type=NodeType.MODULE,
            visibility="pub mod",
            name="submodule_a1",
        ),
    )

    submodule_a2_node = Node(
        id="root::module_a::submodule_a2",
        attributes=NodeAttributes(
            label="pub mod|submodule_a2",
            fillcolor="#a5d987",
            node_type=NodeType.MODULE,
            visibility="pub mod",
            name="submodule_a2",
        ),
    )

    submodule_b1_node = Node(
        id="root::module_b::submodule_b1",
        attributes=NodeAttributes(
            label="pub mod|submodule_b1",
            fillcolor="#ffe082",
            node_type=NodeType.MODULE,
            visibility="pub mod",
            name="submodule_b1",
        ),
    )

    edge1 = Edge(
        source="root",
        target="root::module_a",
        attributes=EdgeAttributes(
            label="owns",
            color="#000000",
            style="solid",
            constraint=True,
            edge_type=EdgeType.OWNS,
        ),
    )

    edge2 = Edge(
        source="root",
        target="root::module_b",
        attributes=EdgeAttributes(
            label="owns",
            color="#000000",
            style="solid",
            constraint=True,
            edge_type=EdgeType.OWNS,
        ),
    )

    edge3 = Edge(
        source="root::module_a",
        target="root::module_a::submodule_a1",
        attributes=EdgeAttributes(
            label="owns",
            color="#000000",
            style="solid",
            constraint=True,
            edge_type=EdgeType.OWNS,
        ),
    )

    edge4 = Edge(
        source="root::module_a",
        target="root::module_a::submodule_a2",
        attributes=EdgeAttributes(
            label="owns",
            color="#000000",
            style="solid",
            constraint=True,
            edge_type=EdgeType.OWNS,
        ),
    )

    edge5 = Edge(
        source="root::module_b",
        target="root::module_b::submodule_b1",
        attributes=EdgeAttributes(
            label="owns",
            color="#000000",
            style="solid",
            constraint=True,
            edge_type=EdgeType.OWNS,
        ),
    )

    edge6 = Edge(
        source="root::module_a::submodule_a1",
        target="root::module_b::submodule_b1",
        attributes=EdgeAttributes(
            label="uses",
            color="#7f7f7f",
            style="dashed",
            constraint=False,
            edge_type=EdgeType.USES,
        ),
    )

    edge7 = Edge(
        source="root::module_a",
        target="root::module_b",
        attributes=EdgeAttributes(
            label="uses",
            color="#7f7f7f",
            style="dashed",
            constraint=False,
            edge_type=EdgeType.USES,
        ),
    )

    graph = Graph(attributes=graph_attrs)
    graph.add_node(root_node)
    graph.add_node(module_a_node)
    graph.add_node(module_b_node)
    graph.add_node(submodule_a1_node)
    graph.add_node(submodule_a2_node)
    graph.add_node(submodule_b1_node)
    graph.add_edge(edge1)
    graph.add_edge(edge2)
    graph.add_edge(edge3)
    graph.add_edge(edge4)
    graph.add_edge(edge5)
    graph.add_edge(edge6)
    graph.add_edge(edge7)

    return graph