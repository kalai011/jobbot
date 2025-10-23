# db.py
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///local.db")  # fallback for local

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine)

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("telegram_id", Integer, unique=True),
    Column("full_name", String),
    Column("email", String),
    Column("phone", String),
    Column("location", String),
    Column("resume_path", String),
    Column("created_at", TIMESTAMP, server_default=func.now())
)

profiles = Table(
    "profiles", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer),
    Column("skills", Text),
    Column("experience", Text),
    Column("current_ctc", String),
    Column("expected_ctc", String),
    Column("additional_info", Text)
)

jobs = Table(
    "jobs", metadata,
    Column("id", Integer, primary_key=True),
    Column("platform", String),
    Column("job_id", String),
    Column("title", String),
    Column("company", String),
    Column("location", String),
    Column("link", Text),
    Column("raw_html", Text),
    Column("posted_at", TIMESTAMP),
    Column("fetched_at", TIMESTAMP, server_default=func.now()),
    UniqueConstraint('platform', 'job_id', name='uix_platform_jobid')
)

applications = Table(
    "applications", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer),
    Column("job_db_id", Integer),
    Column("status", String),  # pending, filled, submitted, failed
    Column("apply_mode", String),  # auto / semi-auto
    Column("applied_at", TIMESTAMP),
    Column("notes", Text)
)

def init_db():
    metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print("DB initialized")
