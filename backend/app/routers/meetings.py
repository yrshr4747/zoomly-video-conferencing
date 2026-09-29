from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import SessionLocal, get_db
from ..models import ChatMessage, Meeting, Participant, utc_now
from ..realtime import meeting_connections
from ..schemas import ChatCreate, ChatMessageOut, DashboardOut, JoinCreate, MeetingCreate, MeetingOut, ParticipantMediaUpdate, ParticipantOut, ScheduleCreate
from ..services.meetings import create_meeting, get_default_user, get_meeting_or_404, list_recent, list_upcoming, meeting_out

router = APIRouter(prefix="/api", tags=["meetings"])


@router.get("/dashboard", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    return {"user": get_default_user(db), "upcoming_meetings": [meeting_out(m) for m in list_upcoming(db)], "recent_meetings": [meeting_out(m) for m in list_recent(db)]}


@router.post("/meetings", response_model=MeetingOut, status_code=status.HTTP_201_CREATED)
def instant_meeting(payload: MeetingCreate, db: Session = Depends(get_db)):
    return meeting_out(create_meeting(db, payload.title, "instant"))


@router.post("/meetings/schedule", response_model=MeetingOut, status_code=status.HTTP_201_CREATED)
def schedule_meeting(payload: ScheduleCreate, db: Session = Depends(get_db)):
    return meeting_out(create_meeting(db, payload.title, "scheduled", payload.description, payload.scheduled_at, payload.duration))


@router.get("/meetings/upcoming", response_model=list[MeetingOut])
def upcoming_meetings(db: Session = Depends(get_db)):
    return [meeting_out(m) for m in list_upcoming(db)]


@router.get("/meetings/recent", response_model=list[MeetingOut])
def recent_meetings(db: Session = Depends(get_db)):
    return [meeting_out(m) for m in list_recent(db)]


@router.get("/meetings/{meeting_id}", response_model=MeetingOut)
def get_meeting(meeting_id: str, db: Session = Depends(get_db)):
    return meeting_out(get_meeting_or_404(db, meeting_id))


@router.post("/meetings/{meeting_id}/join", response_model=ParticipantOut, status_code=status.HTTP_201_CREATED)
async def join_meeting(meeting_id: str, payload: JoinCreate, db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    if meeting.is_locked:
        raise HTTPException(status_code=403, detail="This meeting is locked by its host")
    participant = Participant(meeting_id=meeting.id, display_name=payload.display_name, role="participant", status="waiting" if meeting.waiting_room_enabled else "active")
    db.add(participant)
    db.commit()
    db.refresh(participant)
    await meeting_connections.broadcast(meeting_id, {"type": "participant_changed"})
    return participant


@router.get("/meetings/{meeting_id}/participants", response_model=list[ParticipantOut])
def participants(meeting_id: str, state: str = "active", db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    return db.query(Participant).filter(Participant.meeting_id == meeting.id, Participant.status == state).order_by(Participant.joined_at).all()


@router.post("/meetings/{meeting_id}/participants/{participant_id}/mute", response_model=ParticipantOut)
async def mute_participant(meeting_id: str, participant_id: int, db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    participant = db.get(Participant, participant_id)
    if not participant or participant.meeting_id != meeting.id:
        raise HTTPException(status_code=404, detail="Participant could not be found")
    participant.is_muted = not participant.is_muted
    db.commit()
    db.refresh(participant)
    await meeting_connections.broadcast(meeting_id, {"type": "participant_changed"})
    return participant


@router.patch("/meetings/{meeting_id}/participants/{participant_id}/media", response_model=ParticipantOut)
async def update_participant_media(meeting_id: str, participant_id: int, payload: ParticipantMediaUpdate, db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    participant = db.get(Participant, participant_id)
    if not participant or participant.meeting_id != meeting.id or participant.status != "active":
        raise HTTPException(status_code=404, detail="Active participant could not be found")
    if payload.is_muted is not None:
        participant.is_muted = payload.is_muted
    if payload.is_video_on is not None:
        participant.is_video_on = payload.is_video_on
    db.commit()
    db.refresh(participant)
    await meeting_connections.broadcast(meeting_id, {"type": "participant_changed"})
    return participant


@router.post("/meetings/{meeting_id}/participants/{participant_id}/admit", response_model=ParticipantOut)
async def admit_participant(meeting_id: str, participant_id: int, db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    participant = db.get(Participant, participant_id)
    if not participant or participant.meeting_id != meeting.id or participant.status != "waiting":
        raise HTTPException(status_code=404, detail="Waiting participant could not be found")
    participant.status = "active"
    db.commit()
    db.refresh(participant)
    await meeting_connections.broadcast(meeting_id, {"type": "participant_changed"})
    return participant


@router.post("/meetings/{meeting_id}/participants/admit-all")
async def admit_all(meeting_id: str, db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    db.query(Participant).filter(Participant.meeting_id == meeting.id, Participant.status == "waiting").update({Participant.status: "active"})
    db.commit()
    await meeting_connections.broadcast(meeting_id, {"type": "participant_changed"})
    return {"status": "admitted"}


@router.post("/meetings/{meeting_id}/participants/{participant_id}/raise-hand", response_model=ParticipantOut)
async def raise_hand(meeting_id: str, participant_id: int, db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    participant = db.get(Participant, participant_id)
    if not participant or participant.meeting_id != meeting.id or participant.status != "active":
        raise HTTPException(status_code=404, detail="Active participant could not be found")
    participant.is_hand_raised = not participant.is_hand_raised
    db.commit()
    db.refresh(participant)
    await meeting_connections.broadcast(meeting_id, {"type": "participant_changed"})
    return participant


@router.post("/meetings/{meeting_id}/participants/{participant_id}/remove", status_code=status.HTTP_204_NO_CONTENT)
async def remove_participant(meeting_id: str, participant_id: int, db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    participant = db.get(Participant, participant_id)
    if not participant or participant.meeting_id != meeting.id:
        raise HTTPException(status_code=404, detail="Participant could not be found")
    participant.status = "removed"
    db.commit()
    await meeting_connections.broadcast(meeting_id, {"type": "participant_changed"})


@router.post("/meetings/{meeting_id}/participants/{participant_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_participant(meeting_id: str, participant_id: int, db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    participant = db.get(Participant, participant_id)
    if not participant or participant.meeting_id != meeting.id:
        raise HTTPException(status_code=404, detail="Participant could not be found")
    participant.status = "left"
    participant.left_at = utc_now()
    db.commit()
    await meeting_connections.broadcast(meeting_id, {"type": "participant_changed"})


@router.post("/meetings/{meeting_id}/mute-all")
async def mute_all(meeting_id: str, db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    db.query(Participant).filter(Participant.meeting_id == meeting.id, Participant.status == "active").update({Participant.is_muted: True})
    db.commit()
    await meeting_connections.broadcast(meeting_id, {"type": "participant_changed"})
    return {"status": "muted"}


@router.post("/meetings/{meeting_id}/lock", response_model=MeetingOut)
async def lock_meeting(meeting_id: str, db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    meeting.is_locked = not meeting.is_locked
    db.commit()
    db.refresh(meeting)
    await meeting_connections.broadcast(meeting_id, {"type": "meeting_changed"})
    return meeting_out(meeting)


@router.get("/meetings/{meeting_id}/messages", response_model=list[ChatMessageOut])
def list_messages(meeting_id: str, viewer_id: str = "", db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    if not viewer_id or len(viewer_id) > 40:
        raise HTTPException(status_code=400, detail="A valid meeting viewer is required")
    return db.query(ChatMessage).filter(
        ChatMessage.meeting_id == meeting.id,
        or_(ChatMessage.recipient_id.is_(None), ChatMessage.sender_id == viewer_id, ChatMessage.recipient_id == viewer_id),
    ).order_by(ChatMessage.created_at).all()


@router.post("/meetings/{meeting_id}/messages", response_model=ChatMessageOut, status_code=status.HTTP_201_CREATED)
async def create_message(meeting_id: str, payload: ChatCreate, db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    message = ChatMessage(
        meeting_id=meeting.id,
        sender=payload.sender,
        sender_id=payload.sender_id,
        recipient_id=payload.recipient_id,
        recipient_name=payload.recipient_name,
        body=payload.body,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    event = {"type": "chat", "message": ChatMessageOut.model_validate(message).model_dump(mode="json")}
    if message.recipient_id:
        await meeting_connections.send_to(meeting_id, message.recipient_id, event)
        if message.sender_id != message.recipient_id:
            await meeting_connections.send_to(meeting_id, message.sender_id, event)
    else:
        await meeting_connections.broadcast(meeting_id, event)
    return message


@router.websocket("/ws/meetings/{meeting_id}")
async def meeting_socket(websocket: WebSocket, meeting_id: str) -> None:
    client_id = websocket.query_params.get("client_id", "")
    if not client_id or len(client_id) > 40:
        await websocket.close(code=4400)
        return
    with SessionLocal() as db:
        if not db.query(Meeting).filter(Meeting.meeting_id == meeting_id).first():
            await websocket.close(code=4404)
            return
    await meeting_connections.connect(meeting_id, client_id, websocket)
    try:
        while True:
            payload = await websocket.receive_json()
            if payload.get("type") == "chat":
                body = " ".join(str(payload.get("body", "")).split())[:500]
                sender = " ".join(str(payload.get("sender", "Guest")).split())[:100] or "Guest"
                if body:
                    await meeting_connections.broadcast(meeting_id, {"type": "chat", "sender": sender, "body": body})
            elif payload.get("type") == "ready":
                await meeting_connections.broadcast(meeting_id, {"type": "peer_joined", "client_id": client_id}, exclude_client_id=client_id)
            elif payload.get("type") == "signal":
                target_id = str(payload.get("target_id", ""))[:40]
                signal = payload.get("signal")
                if target_id and isinstance(signal, dict) and signal.get("type") in {"offer", "answer", "candidate"}:
                    await meeting_connections.send_to(meeting_id, target_id, {"type": "signal", "sender_id": client_id, "signal": signal})
    except WebSocketDisconnect:
        meeting_connections.disconnect(meeting_id, client_id)
        await meeting_connections.broadcast(meeting_id, {"type": "peer_left", "client_id": client_id})
