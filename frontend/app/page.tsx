"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { CalendarPlus, ChevronRight, Clock3, LoaderCircle, Plus, Users, Video } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { MeetingCard } from "@/components/MeetingCard";
import { Toast } from "@/components/Toast";
import { api } from "@/lib/api";
import type { Dashboard, Meeting } from "@/lib/types";

function DashboardContent() {
  const router = useRouter(); const searchParams = useSearchParams();
  const [data, setData] = useState<Dashboard | null>(null); const [error, setError] = useState(""); const [creating, setCreating] = useState(false); const [toast, setToast] = useState("");
  useEffect(() => { api.dashboard().then(setData).catch((err) => setError(err.message)); }, []);
  useEffect(() => { if (searchParams.get("scheduled")) setToast("Meeting scheduled and added to your calendar."); if (searchParams.get("left")) setToast("You left the meeting."); }, [searchParams]);
  async function newMeeting() { setCreating(true); try { const meeting = await api.createInstant(); router.push(`/meeting/${meeting.meeting_id}?host=1&name=Akshat%20Jaipuriar`); } catch (err) { setError(err instanceof Error ? err.message : "Could not create meeting."); } finally { setCreating(false); } }
  async function copyInvite(meeting: Meeting) { await navigator.clipboard.writeText(`${window.location.origin}${meeting.invite_url}`); setToast("Invite link copied to clipboard."); }
  return <AppShell><div className="dashboard"><section className="welcome"><div><p className="eyebrow">Tuesday, September 29</p><h1>Good afternoon, {data?.user.name?.split(" ")[0] ?? "Alex"}</h1><p className="subtitle">Ready to connect? Start a meeting or pick up where you left off.</p></div><div className="time-card"><Clock3 size={20} /><span>{new Intl.DateTimeFormat("en", { hour: "numeric", minute: "2-digit" }).format(new Date())}</span></div></section>
    <section className="actions-grid"><button className="action-card primary-action" onClick={newMeeting} disabled={creating}>{creating ? <LoaderCircle className="spin" size={25} /> : <Plus size={28} />}<strong>{creating ? "Starting..." : "New meeting"}</strong><span>Start an instant meeting</span></button><button className="action-card" onClick={() => router.push("/join")}><Users size={27} /><strong>Join</strong><span>Enter a meeting ID</span></button><button className="action-card" onClick={() => router.push("/schedule")}><CalendarPlus size={27} /><strong>Schedule</strong><span>Plan a future meeting</span></button></section>
    {error && <div className="page-error">{error}</div>}
    <section className="content-section"><div className="section-heading"><div><h2>Upcoming meetings</h2><p>Your next conversations, all in one place.</p></div><button className="text-button" onClick={() => router.push("/schedule")}>Schedule <ChevronRight size={16} /></button></div>{!data ? <div className="loading-row"><LoaderCircle className="spin" size={20} /> Loading your meetings</div> : data.upcoming_meetings.length ? <div className="meeting-list">{data.upcoming_meetings.map((meeting) => <MeetingCard key={meeting.id} meeting={meeting} onCopy={copyInvite} />)}</div> : <div className="empty-state">No upcoming meetings. Give your calendar something to look forward to.</div>}</section>
    <section className="content-section"><div className="section-heading"><div><h2>Recent meetings</h2><p>Jump back into conversations you started.</p></div></div>{data && <div className="meeting-list recent-list">{data.recent_meetings.map((meeting) => <MeetingCard key={meeting.id} meeting={meeting} recent onCopy={copyInvite} />)}</div>}</section>
  </div>{toast && <Toast message={toast} onClose={() => setToast("")} />}</AppShell>;
}

export default function DashboardPage() {
  return <Suspense fallback={<AppShell><div className="loading-row">Loading your dashboard</div></AppShell>}><DashboardContent /></Suspense>;
}
