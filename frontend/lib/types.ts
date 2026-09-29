export type User = { id: number; name: string; email: string; avatar: string | null };

export type Meeting = {
  id: number;
  meeting_id: string;
  title: string;
  description: string;
  meeting_type: "instant" | "scheduled";
  scheduled_at: string | null;
  duration: number;
  status: string;
  waiting_room_enabled: boolean;
  is_locked: boolean;
  invite_token: string;
  invite_url: string;
  created_at: string;
};

export type Participant = {
  id: number;
  display_name: string;
  role: "host" | "participant";
  is_muted: boolean;
  is_video_on: boolean;
  status: "waiting" | "active" | "left" | "removed";
  is_hand_raised: boolean;
  joined_at: string;
};

export type Dashboard = { user: User; upcoming_meetings: Meeting[]; recent_meetings: Meeting[] };

export type ChatMessage = { id: number; sender: string; sender_id: string; recipient_id: string | null; recipient_name: string | null; body: string; created_at: string };
