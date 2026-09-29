from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    avatar: str | None

    model_config = {"from_attributes": True}


class MeetingCreate(BaseModel):
    title: str = Field(default="Instant Meeting", min_length=1, max_length=160)
    meeting_type: str = "instant"


class ScheduleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=1000)
    scheduled_at: datetime
    duration: int = Field(ge=15, le=480)

    @field_validator("scheduled_at")
    @classmethod
    def must_be_future(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("scheduled_at must include a timezone")
        if value <= datetime.now(value.tzinfo):
            raise ValueError("Meeting time must be in the future")
        return value


class JoinCreate(BaseModel):
    display_name: str = Field(min_length=2, max_length=100)

    @field_validator("display_name")
    @classmethod
    def name_is_not_blank(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Display name is required")
        return cleaned


class ParticipantMediaUpdate(BaseModel):
    is_muted: bool | None = None
    is_video_on: bool | None = None


class ChatCreate(BaseModel):
    sender: str = Field(min_length=1, max_length=100)
    sender_id: str = Field(min_length=1, max_length=40)
    recipient_id: str | None = Field(default=None, max_length=40)
    recipient_name: str | None = Field(default=None, max_length=100)
    body: str = Field(min_length=1, max_length=500)

    @field_validator("sender", "body")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("Message text is required")
        return cleaned


class ChatMessageOut(BaseModel):
    id: int
    sender: str
    sender_id: str
    recipient_id: str | None
    recipient_name: str | None
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ParticipantOut(BaseModel):
    id: int
    display_name: str
    role: str
    is_muted: bool
    is_video_on: bool
    status: str
    is_hand_raised: bool
    joined_at: datetime

    model_config = {"from_attributes": True}


class MeetingOut(BaseModel):
    id: int
    meeting_id: str
    title: str
    description: str
    meeting_type: str
    scheduled_at: datetime | None
    duration: int
    status: str
    waiting_room_enabled: bool
    is_locked: bool
    invite_token: str
    invite_url: str
    created_at: datetime


class DashboardOut(BaseModel):
    user: UserOut
    upcoming_meetings: list[MeetingOut]
    recent_meetings: list[MeetingOut]
