from app.resume_rag import (
    create_resume_vector_store,
    search_resume,
)


chunks = [
    """
AWS / CLOUD EXPOSURE
Configured Amazon S3 for static website hosting with CloudFront.
Worked with EC2, VPC, IAM, CloudWatch, subnets,
route tables, and Security Groups.
""",

    """
EduJet LMS
Built using React.js, Node.js, Express.js,
MongoDB, Clerk, and Stripe.
Implemented authentication and payment workflows.
""",

    """
Employee Hub
Built using React.js, Node.js, Express.js,
SQL, and JWT authentication.
Implemented CRUD operations and optimized SQL queries.
""",

    """
CERTIFICATIONS
AWS Cloud Architecting — AWS Academy.
Oracle Agentic AI Foundations Associate.
Java Fundamentals — Oracle Academy.
""",
]


vector_store = create_resume_vector_store(chunks)


query = "What AWS experience does this candidate have?"


results = search_resume(
    vector_store,
    query,
    k=2,
)


print("\nQUERY:")
print(query)


print("\nRETRIEVED CHUNKS:")


for result in results:
    print("\n---")
    print(result.page_content)