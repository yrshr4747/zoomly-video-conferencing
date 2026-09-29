"use client";

import { useEffect, useState } from "react";
import { LoaderCircle } from "lucide-react";
import { MeetingRoom } from "@/components/MeetingRoom";
import { api } from "@/lib/api";
import type { Meeting } from "@/lib/types";

export default function MeetingPage({ params, searchParams }: { params: Promise<{ meetingId: string }>; searchParams: Promise<{ name?: string; participant?: string; host?: string; waiting?: string }> }) {
  const [meeting, setMeeting] = useState<Meeting | null>(null); const [error, setError] = useState("");
  const [room, setRoom] = useState({ attendeeName: "Guest", participantId: 0, isHost: false, startsWaiting: false });
  useEffect(() => { Promise.all([params, searchParams]).then(([route, query]) => { setRoom({ attendeeName: query.name ?? "Guest", participantId: Number(query.participant ?? 0), isHost: query.host === "1", startsWaiting: query.waiting === "1" }); return api.meeting(route.meetingId).then(setMeeting); }).catch((err) => setError(err.message)); }, [params, searchParams]);
  if (error) return <div className="room-message">{error}</div>;
  if (!meeting) return <div className="room-message"><LoaderCircle className="spin" /> Loading meeting room</div>;
  return <MeetingRoom meeting={meeting} {...room} />;
}
