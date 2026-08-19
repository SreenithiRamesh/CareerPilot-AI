import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from app.database import Base

# Import all application models so Alembic can discover them.
from app.models import (  # noqa: F401
    CareerPlan,
    CareerProfile,
    Conversation,
    JobDescription,
    JobMatchResult,
    Resume,
    SkillGapReport,
    User,
)


load_dotenv()


config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError(
        "DATABASE_URL is not configured in the environment."
    )


config.set_main_option(
    "sqlalchemy.url",
    database_url,
)


target_metadata = Base.metadata


# --------------------------------------------------
# LangGraph-managed tables
# --------------------------------------------------
#
# These tables are created and maintained by
# langgraph-checkpoint-mysql.
#
# Alembic must ignore them completely so that
# autogenerate does not try to delete or modify them.
#

LANGGRAPH_TABLES = {
    "checkpoints",
    "checkpoint_blobs",
    "checkpoint_writes",
    "checkpoint_migrations",
}


def include_object(
    object_,
    name,
    type_,
    reflected,
    compare_to,
):
    """
    Tell Alembic which database objects it should manage.

    CareerPilot SQLAlchemy models are managed by Alembic.

    LangGraph checkpoint tables are managed by
    langgraph-checkpoint-mysql and must be ignored.
    """

    if (
        type_ == "table"
        and name in LANGGRAPH_TABLES
    ):
        return False

    return True


def run_migrations_offline() -> None:
    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {},
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()

else:
    run_migrations_online()