"use client";

import { CheckCircle2, X } from "lucide-react";

export function Toast({ message, onClose }: { message: string; onClose: () => void }) {
  return <div className="toast" role="status"><CheckCircle2 size={19} /><span>{message}</span><button onClick={onClose} aria-label="Dismiss"><X size={16} /></button></div>;
}
