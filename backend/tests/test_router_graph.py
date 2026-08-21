from app.router_graph import career_router_graph


def test_career_router_graph_is_available():
    """
    Smoke test confirming that the CareerPilot
    routing graph can be imported successfully
    without making a live Gemini request.
    """

    assert career_router_graph is not None