import os

os.environ["DATABASE_URL"] = "sqlite:///./test_zoom.db"

from fastapi.testclient import TestClient

from app.main import app


def test_dashboard_and_meeting_lifecycle():
    with TestClient(app) as client:
        dashboard = client.get("/api/dashboard")
        assert dashboard.status_code == 200
        assert len(dashboard.json()["upcoming_meetings"]) >= 1

        created = client.post("/api/meetings", json={"title": "Test meeting"})
        assert created.status_code == 201
        meeting = created.json()
        assert len(meeting["meeting_id"]) == 10

        joined = client.post(f"/api/meetings/{meeting['meeting_id']}/join", json={"display_name": "Taylor Reed"})
        assert joined.status_code == 201
        assert joined.json()["display_name"] == "Taylor Reed"
        assert joined.json()["status"] == "waiting"

        participant_id = joined.json()["id"]
        waiting = client.get(f"/api/meetings/{meeting['meeting_id']}/participants?state=waiting")
        assert len(waiting.json()) == 1

        admitted = client.post(f"/api/meetings/{meeting['meeting_id']}/participants/{participant_id}/admit")
        assert admitted.status_code == 200
        assert admitted.json()["status"] == "active"

        with client.websocket_connect(f"/api/ws/meetings/{meeting['meeting_id']}?client_id=test-listener") as socket:
            muted = client.post(f"/api/meetings/{meeting['meeting_id']}/participants/{participant_id}/mute")
            assert muted.status_code == 200
            assert socket.receive_json()["type"] == "participant_changed"
            media = client.patch(f"/api/meetings/{meeting['meeting_id']}/participants/{participant_id}/media", json={"is_muted": False, "is_video_on": False})
            assert media.status_code == 200
            assert media.json()["is_video_on"] is False
            assert socket.receive_json()["type"] == "participant_changed"

        with client.websocket_connect(f"/api/ws/meetings/{meeting['meeting_id']}?client_id=host") as host_socket:
            with client.websocket_connect(f"/api/ws/meetings/{meeting['meeting_id']}?client_id=guest") as guest_socket:
                guest_socket.send_json({"type": "ready"})
                assert host_socket.receive_json() == {"type": "peer_joined", "client_id": "guest"}
                host_socket.send_json({"type": "signal", "target_id": "guest", "signal": {"type": "offer", "sdp": "test-offer"}})
                assert guest_socket.receive_json() == {"type": "signal", "sender_id": "host", "signal": {"type": "offer", "sdp": "test-offer"}}

        locked = client.post(f"/api/meetings/{meeting['meeting_id']}/lock")
        assert locked.status_code == 200
        assert locked.json()["is_locked"] is True
        assert client.post(f"/api/meetings/{meeting['meeting_id']}/join", json={"display_name": "Blocked User"}).status_code == 403

        assert client.get("/api/meetings/not-a-meeting").status_code == 404
