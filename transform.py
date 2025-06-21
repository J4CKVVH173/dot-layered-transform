#!/usr/bin/env python3
"""
Script to transform a DOT diagram: groups nodes into domain, application, infrastructure clusters,
adds layout attributes, and filters edges to show only specific interactions:
  - "owns" from root to layers
  - "uses" between layers
  - "owns" within layers
"""
import re
import argparse

# Regex patterns for parsing
NODE_RE = re.compile(
    r'^\s*"(?P<id>[^"]+)"\s*\[label\s*=\s*"(?P<label>[^"]+)"(?:\s*,\s*fillcolor\s*=\s*"(?P<fillcolor>[^"]+)")?'
)
EDGE_RE = re.compile(
    r'^\s*"(?P<src>[^"]+)"\s*->\s*"(?P<tgt>[^"]+)"\s*\[(?P<attrs>[^\]]+)\]'
)
LABEL_RE = re.compile(r'label\s*=\s*"([^"]+)"')

# Layer names are constants
LAYER_NAMES = ["domain", "application", "infrastructure"]


def parse_dot(lines):
    graph_label = None
    nodes = {}
    edges = []
    for line in lines:
        # Capture graph label (first label= outside nodes/edges)
        if (
            "label=" in line
            and "->" not in line
            and "node" not in line
            and "graph" not in line
        ):
            lbl = LABEL_RE.search(line)
            if lbl and not graph_label:
                graph_label = lbl.group(1)
        # Node definition
        m = NODE_RE.match(line)
        if m:
            nid = m.group("id")
            nodes[nid] = {
                "label": m.group("label"),
                "fillcolor": m.group("fillcolor") or "#ffffff",
            }
            continue
        # Edge definition
        e = EDGE_RE.match(line)
        if e:
            attrs = e.group("attrs")
            label = LABEL_RE.search(attrs)
            edges.append(
                (e.group("src"), e.group("tgt"), label.group(1) if label else "")
            )
    return graph_label, nodes, edges


def categorize(nodes):
    roots = []
    layers = {ln: [] for ln in LAYER_NAMES}
    for nid in nodes:
        assigned = False
        for ln in LAYER_NAMES:
            if f"::{ln}" in nid:
                layers[ln].append(nid)
                assigned = True
                break
        if not assigned:
            roots.append(nid)
    return roots, layers


def build_dot(label, nodes, roots, layers, edges):
    out = []
    out.append("digraph {")
    out.append("    graph [")
    out.append(f'        label="{label}",')
    out.append("        labelloc=t,")
    out.append("        pad=0.4,")
    out.append("        layout=dot,")
    out.append("        overlap=false,")
    out.append('        splines="spline",')
    out.append("        rankdir=TB,")
    out.append('        fontname="Helvetica",')
    out.append('        fontsize="36"')
    out.append("    ];")
    out.append("    node [")
    out.append('        fontname="monospace",')
    out.append('        fontsize="10",')
    out.append('        shape="record",')
    out.append('        style="filled"')
    out.append("    ];")
    out.append("    edge [")
    out.append('        fontname="monospace",')
    out.append('        fontsize="10"')
    out.append("    ];")

    # Root node(s)
    for r in roots:
        props = nodes[r]
        out.append(
            f'    "{r}" [label="{props["label"]}", fillcolor="{props["fillcolor"]}", rank=0];'
        )
    out.append("")

    # Layer clusters
    for ln, nids in layers.items():
        out.append(f"    subgraph cluster_{ln} {{")
        out.append(f'        label="{ln}";')
        out.append("        style=rounded;")
        out.append('        color="#f8c04c";')
        out.append("        rank=same;")
        for nid in nids:
            out.append(f'        "{nid}";')
        out.append("    }")
    out.append("")

    # Node definitions for non-root
    for nid, props in nodes.items():
        if nid in roots:
            continue
        out.append(
            f'    "{nid}" [label="{props["label"]}", fillcolor="{props["fillcolor"]}"];'
        )
    out.append("")

    # Filter and emit edges
    for src, tgt, lbl in edges:
        # Determine layers
        src_layer = next((ln for ln in LAYER_NAMES if f"::{ln}" in src), None)
        tgt_layer = next((ln for ln in LAYER_NAMES if f"::{ln}" in tgt), None)
        # Root to layer owns
        if src in roots and tgt_layer and lbl == "owns":
            out.append(f'    "{src}" -> "{tgt}" [label="{lbl}"];')
        # Inter-layer uses
        elif src_layer and tgt_layer and src_layer != tgt_layer and lbl == "uses":
            out.append(f'    "{src}" -> "{tgt}" [label="{lbl}", style=dashed];')
        # Owns within layer
        elif src_layer == tgt_layer and lbl == "owns":
            out.append(f'    "{src}" -> "{tgt}" [label="{lbl}"];')
    out.append("}")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(
        description="Transform a DOT graph into layered clusters."
    )
    parser.add_argument("input", help="Input DOT file")
    parser.add_argument("output", help="Output DOT file")
    args = parser.parse_args()

    with open(args.input) as f:
        lines = f.readlines()

    label, nodes, edges = parse_dot(lines)
    roots, layers = categorize(nodes)
    new_dot = build_dot(label, nodes, roots, layers, edges)

    with open(args.output, "w") as f:
        f.write(new_dot)


if __name__ == "__main__":
    main()
