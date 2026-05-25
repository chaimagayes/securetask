from __future__ import with_statement
import sys
import os
from alembic import context
from sqlalchemy import engine_from_config, pool

# ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

config = context.config

try:
    from src.main import create_web_app
    from src.task_management.db import db

    app = create_web_app()
    with app.app_context():
        target_metadata = db.metadata

        def run_migrations_offline():
            url = config.get_main_option("sqlalchemy.url")
            context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
            with context.begin_transaction():
                context.run_migrations()

        def run_migrations_online():
            # Prefer Flask-SQLAlchemy engine when available
            try:
                connectable = db.get_engine(app)
            except Exception:
                connectable = engine_from_config(config.get_section(config.config_ini_section), prefix='sqlalchemy.', poolclass=pool.NullPool)

            with connectable.connect() as connection:
                context.configure(connection=connection, target_metadata=target_metadata)
                with context.begin_transaction():
                    context.run_migrations()

        if context.is_offline_mode():
            run_migrations_offline()
        else:
            run_migrations_online()
except Exception:
    # If something goes wrong creating the app, fallback to a no-op env so
    # `flask db` commands fail gracefully instead of raising ImportError.
    target_metadata = None
    def run_migrations_offline():
        context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True)
        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online():
        # no-op
        return

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
