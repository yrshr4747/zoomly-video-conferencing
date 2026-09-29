import type { ChatMessage, Dashboard, Meeting, Participant } from "./types";

// On a phone or another laptop, 127.0.0.1 points to that device rather than
// the computer running the API. Use the current hostname unless deployment
// provides an explicit public API URL.
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? (typeof window === "undefined" ? "http://127.0.0.1:8000" : `http://${window.location.hostname}:8000`);
export const wsUrl = apiUrl.replace(/^http/, "ws");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? "Something went wrong. Please try again.");
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  dashboard: () => request<Dashboard>("/api/dashboard"),
  meeting: (meetingId: string) => request<Meeting>(`/api/meetings/${meetingId}`),
  createInstant: (title = "Instant Meeting") => request<Meeting>("/api/meetings", { method: "POST", body: JSON.stringify({ title }) }),
  schedule: (payload: { title: string; description: string; scheduled_at: string; duration: number }) => request<Meeting>("/api/meetings/schedule", { method: "POST", body: JSON.stringify(payload) }),
  join: (meetingId: string, displayName: string) => request<Participant>(`/api/meetings/${meetingId}/join`, { method: "POST", body: JSON.stringify({ display_name: displayName }) }),
  participants: (meetingId: string, state = "active") => request<Participant[]>(`/api/meetings/${meetingId}/participants?state=${state}`),
  mute: (meetingId: string, participantId: number) => request<Participant>(`/api/meetings/${meetingId}/participants/${participantId}/mute`, { method: "POST" }),
  updateMedia: (meetingId: string, participantId: number, payload: { is_muted?: boolean; is_video_on?: boolean }) => request<Participant>(`/api/meetings/${meetingId}/participants/${participantId}/media`, { method: "PATCH", body: JSON.stringify(payload) }),
  remove: (meetingId: string, participantId: number) => request<void>(`/api/meetings/${meetingId}/participants/${participantId}/remove`, { method: "POST" }),
  admit: (meetingId: string, participantId: number) => request<Participant>(`/api/meetings/${meetingId}/participants/${participantId}/admit`, { method: "POST" }),
  admitAll: (meetingId: string) => request<{ status: string }>(`/api/meetings/${meetingId}/participants/admit-all`, { method: "POST" }),
  raiseHand: (meetingId: string, participantId: number) => request<Participant>(`/api/meetings/${meetingId}/participants/${participantId}/raise-hand`, { method: "POST" }),
  leave: (meetingId: string, participantId: number) => request<void>(`/api/meetings/${meetingId}/participants/${participantId}/leave`, { method: "POST" }),
  muteAll: (meetingId: string) => request<{ status: string }>(`/api/meetings/${meetingId}/mute-all`, { method: "POST" }),
  lock: (meetingId: string) => request<Meeting>(`/api/meetings/${meetingId}/lock`, { method: "POST" }),
  messages: (meetingId: string, viewerId: string) => request<ChatMessage[]>(`/api/meetings/${meetingId}/messages?viewer_id=${encodeURIComponent(viewerId)}`),
  sendMessage: (meetingId: string, payload: { sender: string; sender_id: string; recipient_id: string | null; recipient_name: string | null; body: string }) => request<ChatMessage>(`/api/meetings/${meetingId}/messages`, { method: "POST", body: JSON.stringify(payload) }),
};
