from graph import build_graph

if __name__ == "__main__":
    graph = build_graph()

    # Export to DOT (Graphviz format)
    dot_str = graph.get_graph().draw_mermaid()
    print(dot_str)
