from app.graph import career_graph


def test_career_graph_is_available():
    """
    Smoke test confirming that the CareerPilot
    base LangGraph workflow can be imported
    successfully without invoking Gemini.
    """

    assert career_graph is not None