from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add the app directory to the path to import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import *  # Import all models
from app.database import Base

config = context.config

# Set up loggers
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_database_url():
    # Always use synchronous pymysql driver for Alembic
    url = os.getenv("DATABASE_URL", "mysql+pymysql://pet_user:pet_password@mysql:3306/pet_adoption")
    # If mistakenly using aiomysql, convert it automatically
    if "mysql+aiomysql" in url:
        url = url.replace("mysql+aiomysql", "mysql+pymysql")
    return url

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    url = get_database_url()
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
