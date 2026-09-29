import { AppShell } from "@/components/AppShell";
import { JoinForm } from "@/components/JoinForm";

export default function JoinPage() { return <AppShell><div className="standalone-page"><div className="page-intro"><p className="eyebrow">Join a meeting</p><h1>Connect to your team</h1><p className="subtitle">Enter the meeting ID shared with you and choose how you would like to appear.</p></div><JoinForm /></div></AppShell>; }
