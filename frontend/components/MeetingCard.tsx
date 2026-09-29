import Link from "next/link";
import { ArrowUpRight, CalendarClock, Clock3, Copy, Video } from "lucide-react";
import type { Meeting } from "@/lib/types";

function formatDate(date: string | null) {
  if (!date) return "Started recently";
  return new Intl.DateTimeFormat("en", { weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(date));
}

export function MeetingCard({ meeting, recent = false, onCopy }: { meeting: Meeting; recent?: boolean; onCopy: (meeting: Meeting) => void }) {
  return <article className="meeting-card">
    <div className="meeting-icon"><CalendarClock size={20} /></div>
    <div className="meeting-body"><div className="meeting-heading"><h3>{meeting.title}</h3><button onClick={() => onCopy(meeting)} className="copy-button" aria-label="Copy invite link"><Copy size={16} /></button></div><p>{recent ? "Instant meeting" : formatDate(meeting.scheduled_at)} <span className="dot">.</span> {meeting.duration} min</p><span className="meeting-id">ID: {meeting.meeting_id}</span></div>
    <Link href={`/join/${meeting.meeting_id}?token=${meeting.invite_token}`} className="join-link">{recent ? <Video size={17} /> : <ArrowUpRight size={17} />}<span>{recent ? "Join" : "Details"}</span></Link>
  </article>;
}
