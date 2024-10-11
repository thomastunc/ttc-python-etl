import os
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv
from alembic.ddl.impl import DefaultImpl

from src.db import model  # Importeer je modellen


# Aangepaste Alembic implementatieklasse voor DuckDB
class AlembicDuckDBImpl(DefaultImpl):
    """Alembic implementation for DuckDB."""
    __dialect__ = "duckdb"


# Laad de .env variabelen
load_dotenv()

# Haal de database URL op uit de .env file
db_url = os.getenv("DATABASE_URL")

# Dit is de Alembic Config object
config = context.config

# Stel de database-URL in voor de Alembic-configuratie
config.set_main_option("sqlalchemy.url", db_url)

# Logging instellen
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Voeg je model's MetaData object hier toe voor 'autogenerate' support
target_metadata = model.Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'online' mode."""
    # Maak de engine aan via de URL uit de .env
    connectable = create_engine(db_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Voer altijd migraties in offline mode uit
run_migrations_offline()
