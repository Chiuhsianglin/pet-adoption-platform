from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

import os
import sys
import asyncio

# Add the app directory to the path to import models
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import *  # Import all models
from app.database import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Get database URL from environment variable
    url = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost/pet_adoption")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get database URL from environment variable
    database_url = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost/pet_adoption")
    
    # Override the sqlalchemy.url in configuration
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


def run_async_migrations() -> None:
    """Run migrations in async mode for async engines."""
    async def do_run_migrations(connection):
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        async with context.begin_transaction():
            await context.run_migrations()

    async def run():
        database_url = os.getenv("DATABASE_URL", "mysql+aiomysql://user:password@localhost/pet_adoption")
        # Convert sync URL to async if needed
        if "mysql+pymysql" in database_url:
            database_url = database_url.replace("mysql+pymysql", "mysql+aiomysql")
        
        engine = create_async_engine(database_url)
        
        async with engine.connect() as connection:
            await do_run_migrations(connection)
        
        await engine.dispose()

    asyncio.run(run())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
