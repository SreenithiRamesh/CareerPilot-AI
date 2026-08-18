from router_graph import career_router_graph


message = """
Please review my resume.
I am a 2026 CSE graduate.
Skills: Java, React, Node.js, SQL, AWS.
Projects: LMS application and Employee Management System.
I am targeting Software Engineer roles.
"""

result = career_router_graph.invoke(
    {
        "message": message,
        "intent": "",
        "response": "",
    }
)

print("USER:")
print(message)

print("INTENT:")
print(result["intent"])

print("RESPONSE:")
print(result["response"])