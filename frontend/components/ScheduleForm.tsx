"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { CalendarPlus, LoaderCircle } from "lucide-react";
import { api } from "@/lib/api";

export function ScheduleForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [startsAt, setStartsAt] = useState("");
  const [duration, setDuration] = useState("30");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (!startsAt) return setError("Choose when your meeting starts.");
    setSaving(true);
    try {
      await api.schedule({ title, description, scheduled_at: new Date(startsAt).toISOString(), duration: Number(duration) });
      router.push("/?scheduled=1");
    } catch (err) { setError(err instanceof Error ? err.message : "Could not schedule the meeting."); } finally { setSaving(false); }
  }

  return <form className="form-card schedule-form" onSubmit={submit}>
    <label>Meeting title<input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Design review" required /></label>
    <label>Description <span className="optional">optional</span><textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="What is this meeting about?" rows={4} /></label>
    <div className="form-grid"><label>Date and time<input type="datetime-local" value={startsAt} onChange={(e) => setStartsAt(e.target.value)} required /></label><label>Duration<select value={duration} onChange={(e) => setDuration(e.target.value)}><option value="15">15 minutes</option><option value="30">30 minutes</option><option value="45">45 minutes</option><option value="60">1 hour</option></select></label></div>
    {error && <p className="form-error">{error}</p>}
    <button className="primary-button form-submit" disabled={saving}>{saving ? <LoaderCircle className="spin" size={18} /> : <CalendarPlus size={18} />}Schedule meeting</button>
  </form>;
}
