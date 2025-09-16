import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from logging.config import fileConfig

from alembic import context

from sqlalchemy import create_engine

from app.db.base import Base
from app.models import user, permission  # importa modelos

config = context.config
fileConfig(config.config_file_name)


def run_migrations_offline():
    url = os.getenv("SYNC_DATABASE_URL")
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = create_engine(os.getenv("SYNC_DATABASE_URL"))
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
