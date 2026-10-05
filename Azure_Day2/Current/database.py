"""
database.py — everything SQLAlchemy/Azure SQL related lives here, kept separate
from main.py so the app logic (routes) stays readable, same separation you
used in the original FastAPI + DB masterclass notebook.

Uses pymssql instead of pyodbc/ODBC Driver 18 — pymssql is pure pip-installable
(bundles its own driver internals) so there's no Homebrew/system driver step
needed at all, which sidesteps the Homebrew tap-trust issue entirely.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

SERVER = os.environ["AZURE_SQL_SERVER"]      # e.g. az900demo-sqlsrv.database.windows.net
DATABASE = os.environ["AZURE_SQL_DATABASE"]  # e.g. demodb
USERNAME = os.environ["AZURE_SQL_USERNAME"]  # e.g. sqladmin
PASSWORD = os.environ["AZURE_SQL_PASSWORD"]

# URL.create safely escapes special characters in the username/password
# for us, instead of hand-building a connection string.
DATABASE_URL = URL.create(
    drivername="mssql+pymssql",
    username=USERNAME,
    password=PASSWORD,
    host=SERVER,
    port=1433,
    database=DATABASE,
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Vote(Base):
    """One row per vote cast. Deliberately simple: no user accounts, just
    the option text and when it was voted — enough to demonstrate real
    INSERT + GROUP BY queries against Azure SQL Database."""

    __tablename__ = "poll_votes"

    id = Column(Integer, primary_key=True, index=True)
    option_text = Column(String(200), nullable=False)
    voted_at = Column(DateTime(timezone=True), server_default=func.now())


def init_db():
    """Creates the poll_votes table if it doesn't exist yet."""
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
