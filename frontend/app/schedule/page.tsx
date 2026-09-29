import { AppShell } from "@/components/AppShell";
import { ScheduleForm } from "@/components/ScheduleForm";

export default function SchedulePage() { return <AppShell><div className="standalone-page"><div className="page-intro"><p className="eyebrow">Schedule a meeting</p><h1>Make time for what matters</h1><p className="subtitle">Your meeting will get a unique ID and shareable invite link automatically.</p></div><ScheduleForm /></div></AppShell>; }
