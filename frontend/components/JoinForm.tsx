"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Camera, LoaderCircle, Video, VideoOff } from "lucide-react";
import { api } from "@/lib/api";

export function JoinForm({ initialMeetingId = "" }: { initialMeetingId?: string }) {
  const router = useRouter();
  const [meetingId, setMeetingId] = useState(initialMeetingId);
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState("");
  const [joining, setJoining] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const [previewError, setPreviewError] = useState("");
  const previewRef = useRef<HTMLVideoElement>(null);
  const previewStream = useRef<MediaStream | null>(null);
  useEffect(() => setMeetingId(initialMeetingId), [initialMeetingId]);
  useEffect(() => () => previewStream.current?.getTracks().forEach((track) => track.stop()), []);

  async function togglePreview() {
    if (previewStream.current) { previewStream.current.getTracks().forEach((track) => track.stop()); previewStream.current = null; setPreviewing(false); return; }
    try { setPreviewError(""); const stream = await navigator.mediaDevices.getUserMedia({ video: true }); previewStream.current = stream; if (previewRef.current) previewRef.current.srcObject = stream; setPreviewing(true); }
    catch (error) { setPreviewError(error instanceof DOMException && error.name === "NotReadableError" ? "Your camera is busy in another app or browser tab." : "Camera access is blocked for this browser tab."); }
  }

  async function submit(event: FormEvent) {
    event.preventDefault(); setError(""); setJoining(true);
    try { await api.meeting(meetingId.trim()); const participant = await api.join(meetingId.trim(), displayName); router.push(`/meeting/${meetingId.trim()}?name=${encodeURIComponent(displayName)}&participant=${participant.id}&waiting=${participant.status === "waiting" ? "1" : "0"}`); }
    catch (err) { setError(err instanceof Error ? err.message : "Could not join the meeting."); } finally { setJoining(false); }
  }
  return <form className="form-card join-form" onSubmit={submit}>{previewing && <div className="prejoin-preview"><video ref={previewRef} autoPlay muted playsInline /><span>You&apos;re ready to join</span></div>}<button type="button" className="preview-toggle" onClick={togglePreview}>{previewing ? <VideoOff size={17} /> : <Camera size={17} />}{previewing ? "Turn off preview" : "Preview camera and mic"}</button><label>Meeting ID or personal link name<input value={meetingId} onChange={(e) => setMeetingId(e.target.value)} placeholder="Enter meeting ID" required /></label><label>Your display name<input value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="How should people see you?" required minLength={2} /></label>{(error || previewError) && <p className="form-error">{error || previewError}</p>}<button className="primary-button form-submit" disabled={joining}>{joining ? <LoaderCircle className="spin" size={18} /> : <Video size={18} />}Join</button></form>;
}
