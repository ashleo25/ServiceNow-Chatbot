export interface Message {
  id: string;
  message: string;
  timestamp: string;
  is_user: boolean;
}

export interface ChatHistory {
  id: string;
  title: string;
  messages: Message[];
  lastMessage: string;
  timestamp: string;
}

export interface TicketSearchResult {
  ticket_id: string;
  title: string;
  description: string;
  status: string;
  similarity_score: number;
  resolution?: string;
}