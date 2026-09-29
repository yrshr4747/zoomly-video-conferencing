import { AppShell } from "@/components/AppShell";
import { JoinForm } from "@/components/JoinForm";

export default async function PreJoinPage({ params }: { params: Promise<{ meetingId: string }> }) { const { meetingId } = await params; return <AppShell><div className="standalone-page"><div className="page-intro"><p className="eyebrow">You&apos;re invited</p><h1>Join this meeting</h1><p className="subtitle">Choose a display name to enter the meeting room.</p></div><JoinForm initialMeetingId={meetingId} /></div></AppShell>; }
