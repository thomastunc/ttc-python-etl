import os
from sqlalchemy import create_engine
from src.db.model import Base


def get_engine():
    db_url = os.getenv('DATABASE_URL')

    # Als je een relatieve URL wilt verwerken
    if db_url.startswith("duckdb:///"):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_relative_path = db_url.replace("duckdb:///", "")
        db_url = f"duckdb:///{os.path.join(project_root, db_relative_path)}"

    return create_engine(db_url)


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Database succesvol geïnitialiseerd!")
