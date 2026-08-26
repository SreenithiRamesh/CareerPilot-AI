from app.agent_tools import (
    CAREERPILOT_AGENT_TOOLS,
)
from app.tool_agent_graph import (
    tool_agent_graph,
)


def test_agent_tool_registry():
    tool_names = {
        tool.name
        for tool in CAREERPILOT_AGENT_TOOLS
    }

    expected_tools = {
        "get_resume_context",
        "get_latest_job_match",
        "get_latest_skill_gap",
        "generate_career_plan",
        "recommend_project",
        "prepare_interview_focus",
    }

    assert tool_names == expected_tools


def test_tool_agent_graph_compiles():
    assert tool_agent_graph is not None