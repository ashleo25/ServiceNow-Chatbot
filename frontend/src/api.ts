// Types
interface Message {
  id: string;
  message: string;
  timestamp: string;
  is_user: boolean;
}

interface TicketSearchResult {
  ticket_id: string;
  title: string;
  description: string;
  status: string;
  similarity_score: number;
  resolution?: string;
}

const API_BASE_URL = 'http://localhost:8001';

export class ChatAPI {
  private static instance: ChatAPI;
  
  public static getInstance(): ChatAPI {
    if (!ChatAPI.instance) {
      ChatAPI.instance = new ChatAPI();
    }
    return ChatAPI.instance;
  }

  async sendMessage(userId: string, message: string): Promise<{ response: string; message_id: string }> {
    const response = await fetch(`${API_BASE_URL}/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        id: crypto.randomUUID(),
        user_id: userId,
        message,
        timestamp: new Date().toISOString(),
        is_user: true,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    return response.json();
  }

  async getChatHistory(userId: string): Promise<Message[]> {
    const response = await fetch(`${API_BASE_URL}/chat/history/${userId}`);
    
    if (!response.ok) {
      throw new Error('Failed to get chat history');
    }

    const data = await response.json();
    return data.messages || [];
  }

  async searchTickets(description: string): Promise<TicketSearchResult[]> {
    const response = await fetch(`${API_BASE_URL}/tickets/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ description }),
    });

    if (!response.ok) {
      throw new Error('Failed to search tickets');
    }

    const data = await response.json();
    return data.tickets || [];
  }

  async createTicket(userId: string, title: string, description: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/tickets/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        title,
        description,
        priority: '3',
        category: 'general',
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to create ticket');
    }

    return response.json();
  }

  async getUserTickets(userId: string): Promise<any[]> {
    const response = await fetch(`${API_BASE_URL}/tickets/user/${userId}`);
    
    if (!response.ok) {
      throw new Error('Failed to get user tickets');
    }

    const data = await response.json();
    return data.tickets || [];
  }
}