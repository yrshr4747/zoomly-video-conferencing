"use client";

import Link from "next/link";
import { CalendarDays, Clock3, Home, Settings, Video } from "lucide-react";

export function AppShell({ children }: { children: React.ReactNode }) {
  return <div className="app-shell">
    <aside className="sidebar">
      <Link href="/" className="brand"><span className="brand-mark"><Video size={19} fill="currentColor" /></span><span>zoomly</span></Link>
      <nav>
        <Link href="/" className="nav-item active"><Home size={19} />Home</Link>
        <Link href="/schedule" className="nav-item"><CalendarDays size={19} />Meetings</Link>
        <span className="nav-item muted"><Clock3 size={19} />History</span>
      </nav>
      <div className="sidebar-bottom"><span className="nav-item muted"><Settings size={19} />Settings</span><div className="profile"><span className="avatar">AJ</span><span><strong>Akshat Jaipuriar</strong><small>Basic</small></span></div></div>
    </aside>
    <main className="main-content"><header className="topbar"><span className="mobile-brand">zoomly</span><div className="topbar-actions"><button className="icon-button" aria-label="Help">?</button><span className="avatar avatar-small">AJ</span></div></header>{children}</main>
  </div>;
}
