from app.graph.graph import ReviewGraph


def test_graph_initialization():
    graph = ReviewGraph()
    graph.add_node("review")
    assert graph.nodes == ["review"]
