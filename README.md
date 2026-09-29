# Zoomly

A focused Zoom-style meeting platform built for a full-stack assessment. It supports a seeded dashboard, instant meeting creation, validated joining, scheduled meetings, shareable invite links, real local device previews, a host-controlled waiting room, and realtime room coordination.

## Stack

- Frontend: Next.js App Router, React, TypeScript, CSS, Lucide icons
- Backend: FastAPI, Pydantic, SQLAlchemy
- Database: SQLite

## Architecture

`Next.js UI -> REST API -> FastAPI routers/services -> SQLAlchemy -> SQLite`

The frontend owns presentation and client interaction. `frontend/lib/api.ts` is the only browser API layer. FastAPI owns input validation and meeting lifecycle rules; the service layer generates meeting IDs and invite tokens before persistence.

## Database Design

- `users`: the default signed-in user; retained as a real entity so authentication can be added later.
- `meetings`: hosted by one user, with a unique 10-digit `meeting_id` and a unique secure `invite_token`. It stores meeting type, scheduling details, and status.
- `participants`: per-meeting join sessions. It records a nullable user relation, display name, host/participant role, media state, and join/leave timestamps.
- Meeting records also contain the waiting-room and lock state. Participant records retain a lifecycle state (`waiting`, `active`, `left`, or `removed`) and hand-raise state instead of being deleted when a guest exits.

`meetings.host_id -> users.id` and `participants.meeting_id -> meetings.id` are foreign keys. Meeting IDs, invite tokens, meeting dates, host IDs, and participant meeting IDs are indexed where appropriate.

## API

- `GET /api/dashboard` - default user, upcoming meetings, recent meetings
- `POST /api/meetings` - create an instant meeting
- `POST /api/meetings/schedule` - schedule a persisted meeting
- `GET /api/meetings/{meeting_id}` - validate/get a meeting
- `POST /api/meetings/{meeting_id}/join` - create a participant session
- `GET /api/meetings/{meeting_id}/participants` - active participants
- `POST /api/meetings/{meeting_id}/participants/{participant_id}/mute` - toggle participant mute state
- `PATCH /api/meetings/{meeting_id}/participants/{participant_id}/media` - synchronize a guest's own microphone/video state
- `POST /api/meetings/{meeting_id}/participants/{participant_id}/admit` - admit a waiting guest
- `POST /api/meetings/{meeting_id}/participants/admit-all` - admit every waiting guest
- `POST /api/meetings/{meeting_id}/participants/{participant_id}/remove` - remove a participant
- `POST /api/meetings/{meeting_id}/participants/{participant_id}/raise-hand` - toggle a guest hand raise
- `POST /api/meetings/{meeting_id}/mute-all` - host mute-all action
- `POST /api/meetings/{meeting_id}/lock` - toggle meeting lock
- `WS /api/ws/meetings/{meeting_id}` - realtime room presence refreshes and chat messages

## Run Locally

Start the API in one terminal:

```bash
cd /Users/yashrajsingh/Documents/ChatGPT/zoom/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --env-file .env --reload
```

The database is created and seeded automatically at API startup. The seed is idempotent.

Start the web app in another terminal:

```bash
cd /Users/yashrajsingh/Documents/ChatGPT/zoom/frontend
cp .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`. Configure the API URL with `NEXT_PUBLIC_API_URL`; configure the API database path and CORS origin with `DATABASE_URL` and `FRONTEND_ORIGIN`. Both `localhost` and `127.0.0.1` loopback origins are allowed by default for local development.

## Two-person Demo

Use two separate browser profiles or devices. This prevents one computer camera or microphone from being claimed by more than one tab.

1. Start the API with `uvicorn app.main:app --host 0.0.0.0 --port 8000` and the frontend with `npm run dev -- --hostname 0.0.0.0 --port 3000`.
2. On the host computer, find its Wi-Fi address with `ipconfig getifaddr en0`, then open `http://YOUR_WIFI_IP:3000`.
3. Create a meeting as Akshat, click **Copy invite**, and open the copied link on a phone or another laptop connected to the same Wi-Fi.
4. Join with a guest name. The guest stays in the waiting room. On the host page, open **Participants** and choose **Admit** or **Admit all**.
5. In the room, unmute the microphone, watch the green input meter move, click **Test speaker**, send chat messages, raise/lower the guest hand, and use host mute/remove/lock controls.

## Deployment

Deploy the FastAPI backend from `render.yaml` as a Render Blueprint. Set `FRONTEND_ORIGIN_REGEX` to the exact deployed frontend origin, for example `^https://zoomly-web.vercel.app$`. The free deployment uses an ephemeral SQLite file, so the seeded dashboard returns after backend restarts. Attach a persistent disk or move to PostgreSQL when durable production data is required.

Deploy the `frontend` directory as a Next.js project on Vercel. Set `NEXT_PUBLIC_API_URL` to the HTTPS Render API URL, then redeploy the frontend. HTTPS is required for phone camera and microphone permissions.

## Assumptions and Limits

- Authentication is intentionally omitted; Akshat Jaipuriar is the seeded default host.
- Camera, microphone, and screen-share controls use the browser MediaDevices APIs. A WebRTC mesh sends media directly between active browser peers, with FastAPI WebSockets relaying offers, answers, and ICE candidates.
- The mesh is intentionally suitable for a small assessment demo. A production multi-party service would retain the signalling layer but replace peer-to-peer fan-out with TURN and an SFU such as LiveKit or mediasoup.
- SQLite is appropriate for this assessment and local deployment. A production multi-instance deployment should migrate to PostgreSQL and introduce authenticated users, real-time signalling, and media infrastructure.

## Verification

```bash
cd backend
pytest

cd ../frontend
npm run build
```

## Interview Notes

1. **Why Next.js?** App Router provides clear route boundaries and an easy production build for the frontend.
2. **Why FastAPI?** Pydantic validation, automatic OpenAPI documentation, and concise dependency injection fit a small REST service.
3. **Why SQLite?** It is zero-config and durable for an assessment; SQLAlchemy makes later migration practical.
4. **Why model a default user?** It keeps host relationships correct without adding out-of-scope authentication.
5. **How are meeting IDs safe?** The service generates 10 random digits with `secrets` and verifies uniqueness before insert.
6. **How are invite links protected?** Each meeting gets a separate URL-safe random token; production would validate it on join.
7. **Why a service layer?** It separates persistence/lifecycle logic from HTTP routers, keeping it testable and explainable.
8. **How is a join validated?** The API resolves the meeting before creating a participant and returns a 404 for absent IDs.
9. **How does the dashboard stay accurate?** It always loads persisted meetings from `GET /api/dashboard`.
10. **How would you add WebRTC?** Add authenticated signalling, STUN/TURN infrastructure, and realtime participant events while retaining the meeting model.
11. **How would you scale persistence?** Move the SQLAlchemy URL to PostgreSQL, add migrations, and use stronger transactional uniqueness constraints.
12. **Why is host control currently implicit?** Authentication is deliberately out of scope, so the single default user is treated as host.
