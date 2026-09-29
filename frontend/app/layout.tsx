import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Zoomly | Meetings",
  description: "A polished video meeting workspace",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
