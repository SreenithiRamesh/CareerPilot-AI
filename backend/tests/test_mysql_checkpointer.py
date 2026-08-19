import os

from dotenv import load_dotenv
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver


load_dotenv()


database_url = os.getenv(
    "LANGGRAPH_DATABASE_URL"
)

if not database_url:
    raise RuntimeError(
        "LANGGRAPH_DATABASE_URL is not configured."
    )


with PyMySQLSaver.from_conn_string(
    database_url
) as checkpointer:
    print(
        "MYSQL CHECKPOINTER CONNECTION SUCCESS"
    )

    checkpointer.setup()

    print(
        "MYSQL CHECKPOINTER SETUP SUCCESS"
    )