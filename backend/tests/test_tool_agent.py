from langchain_core.messages import HumanMessage

from app.tool_agent_graph import tool_agent_graph


result = tool_agent_graph.invoke(
    {
        "thread_id": "alex-memory-2",
        "job_description": "",
        "messages": [
            HumanMessage(
                content="What AWS experience does my resume show?"
            )
        ],
    }
)


print("\nFINAL MESSAGES:\n")

for message in result["messages"]:
    print(type(message).__name__)
    print(message.content)
    print("---")