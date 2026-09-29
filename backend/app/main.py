import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from .database import Base, SessionLocal, engine
from .routers.meetings import router
from .services.meetings import seed_database

app = FastAPI(title="Zoomly API", version="1.0.0")
origins = [origin.strip() for origin in os.getenv("FRONTEND_ORIGIN", "http://localhost:3000,http://127.0.0.1:3000").split(",")]
origin_regex = os.getenv(
    "FRONTEND_ORIGIN_REGEX",
    r"^https?://(?:localhost|127\.0\.0\.1|192\.168\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})(?::\d+)?$",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # Permit devices on the same private Wi-Fi network during a local demo.
    allow_origin_regex=origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.on_event("startup")
def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    if engine.url.get_backend_name() == "sqlite":
        with engine.begin() as connection:
            meeting_columns = {column[1] for column in connection.execute(text("PRAGMA table_info(meetings)"))}
            participant_columns = {column[1] for column in connection.execute(text("PRAGMA table_info(participants)"))}
            chat_columns = {column[1] for column in connection.execute(text("PRAGMA table_info(chat_messages)"))} if connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_messages'")) .scalar() else set()
            if "waiting_room_enabled" not in meeting_columns:
                connection.execute(text("ALTER TABLE meetings ADD COLUMN waiting_room_enabled BOOLEAN NOT NULL DEFAULT 1"))
            if "is_locked" not in meeting_columns:
                connection.execute(text("ALTER TABLE meetings ADD COLUMN is_locked BOOLEAN NOT NULL DEFAULT 0"))
            if "status" not in participant_columns:
                connection.execute(text("ALTER TABLE participants ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active'"))
            if "is_hand_raised" not in participant_columns:
                connection.execute(text("ALTER TABLE participants ADD COLUMN is_hand_raised BOOLEAN NOT NULL DEFAULT 0"))
            if chat_columns and "sender_id" not in chat_columns:
                connection.execute(text("ALTER TABLE chat_messages ADD COLUMN sender_id VARCHAR(40) NOT NULL DEFAULT 'host'"))
            if chat_columns and "recipient_id" not in chat_columns:
                connection.execute(text("ALTER TABLE chat_messages ADD COLUMN recipient_id VARCHAR(40)"))
            if chat_columns and "recipient_name" not in chat_columns:
                connection.execute(text("ALTER TABLE chat_messages ADD COLUMN recipient_name VARCHAR(100)"))
    with SessionLocal() as db:
        seed_database(db)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
