from dot_analyzer.core.dot_parser import Node, NodeAttributes, NodeType

CIRCLED_NODES = [
    [
        Node(
            id="root::module_a",
            attributes=NodeAttributes(
                label="pub mod|module_a",
                fillcolor="#81c169",
                node_type=NodeType.MODULE,
                visibility="pub mod",
                name="module_a",
            ),
        ),
        Node(
            id="root::module_b",
            attributes=NodeAttributes(
                label="pub(crate) mod|module_b",
                fillcolor="#f8c04c",
                node_type=NodeType.MODULE,
                visibility="pub(crate) mod",
                name="module_b",
            ),
        ),
        Node(
            id="root::module_c",
            attributes=NodeAttributes(
                label="pub mod|module_c",
                fillcolor="#f4a261",
                node_type=NodeType.MODULE,
                visibility="pub mod",
                name="module_c",
            ),
        ),
        Node(
            id="root::module_a",
            attributes=NodeAttributes(
                label="pub mod|module_a",
                fillcolor="#81c169",
                node_type=NodeType.MODULE,
                visibility="pub mod",
                name="module_a",
            ),
        ),
    ],
]
