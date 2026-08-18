from graph import career_graph


result = career_graph.invoke(
    {
        "message": "I want to prepare for backend engineering.",
        "response": "",
    }
)

print(result)