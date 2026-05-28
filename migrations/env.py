from __future__ import with_statement
import sys
import os
from alembic import context
from sqlalchemy import pool

# ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

config = context.config
from src.main import create_web_app
from src.task_management.db import db

app = create_web_app()
with app.app_context():
    target_metadata = db.metadata


def run_migrations_offline():
    url = app.config.get("SQLALCHEMY_DATABASE_URI")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with app.app_context():
        connectable = db.engine
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )
            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
