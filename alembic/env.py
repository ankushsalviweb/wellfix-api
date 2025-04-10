from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- Custom imports for WellFix ---
import os
import sys
from dotenv import load_dotenv

# Load environment variables directly
load_dotenv()

# Add project root to sys.path to allow finding modules
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR) # Try inserting at the beginning

# Import Base and models directly, avoid importing settings
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Import all model files
from wellfix_api.models import user, address, job, enums, pricing
# --- End Custom imports ---

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- Set database URL directly from environment variable ---
# Get the database URL from environment
database_url = os.environ.get("DATABASE_URL", "sqlite:///./wellfix.db")

# Force SQLite for safety if there's an issue loading from .env
if not database_url or "postgresql" in database_url:
    database_url = "sqlite:///./wellfix.db"
    print(f"Using fallback SQLite database: {database_url}")
else:
    print(f"Using configured database: {database_url}")

config.set_main_option("sqlalchemy.url", database_url)
# --- End DATABASE_URL handling ---

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# --- Use Base from our db setup ---
target_metadata = Base.metadata
# --- End Base handling ---

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
    url = config.get_main_option("sqlalchemy.url")
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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
