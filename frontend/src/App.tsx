import React, { useState, useEffect } from 'react';
import { ChatSidebar } from './components/ChatSidebar';
import { ChatWindow } from './components/ChatWindow';
import { MessageInput } from './components/MessageInput';
import { ChatAPI } from './api';

// Types
interface Message {
  id: string;
  message: string;
  timestamp: string;
  is_user: boolean;
}

interface ChatHistory {
  id: string;
  title: string;
  messages: Message[];
  lastMessage: string;
  timestamp: string;
}

const api = ChatAPI.getInstance();

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [userId] = useState('user123'); // In a real app, this would come from authentication

  // Initialize with a default chat
  useEffect(() => {
    if (chatHistory.length === 0) {
      createNewChat();
    }
  }, []);

  const createNewChat = () => {
    const newChatId = crypto.randomUUID();
    const newChat: ChatHistory = {
      id: newChatId,
      title: 'New Chat',
      messages: [],
      lastMessage: 'New conversation started',
      timestamp: new Date().toISOString(),
    };
    
    setChatHistory(prev => [newChat, ...prev]);
    setCurrentChatId(newChatId);
    setMessages([]);
  };

  const selectChat = (chatId: string) => {
    const chat = chatHistory.find(c => c.id === chatId);
    if (chat) {
      setCurrentChatId(chatId);
      setMessages(chat.messages);
    }
  };

  const updateChatHistory = (chatId: string, newMessages: Message[]) => {
    setChatHistory(prev => prev.map(chat => {
      if (chat.id === chatId) {
        const lastMessage = newMessages.length > 0 
          ? newMessages[newMessages.length - 1].message 
          : 'New conversation started';
        
        // Generate title from first user message
        let title = chat.title;
        if (title === 'New Chat' && newMessages.length > 0) {
          const firstUserMessage = newMessages.find(m => m.is_user);
          if (firstUserMessage) {
            title = firstUserMessage.message.slice(0, 30) + (firstUserMessage.message.length > 30 ? '...' : '');
          }
        }

        return {
          ...chat,
          title,
          messages: newMessages,
          lastMessage,
          timestamp: new Date().toISOString(),
        };
      }
      return chat;
    }));
  };

  const sendMessage = async (messageText: string) => {
    if (!currentChatId) return;

    // Add user message immediately
    const userMessage: Message = {
      id: crypto.randomUUID(),
      message: messageText,
      timestamp: new Date().toISOString(),
      is_user: true,
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      // Send message to API
      const response = await api.sendMessage(userId, messageText);

      // Add bot response
      const botMessage: Message = {
        id: response.message_id,
        message: response.response,
        timestamp: new Date().toISOString(),
        is_user: false,
      };

      const finalMessages = [...newMessages, botMessage];
      setMessages(finalMessages);
      updateChatHistory(currentChatId, finalMessages);

    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        message: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        is_user: false,
      };

      const finalMessages = [...newMessages, errorMessage];
      setMessages(finalMessages);
      updateChatHistory(currentChatId, finalMessages);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-white">
      <ChatSidebar
        chatHistory={chatHistory}
        currentChatId={currentChatId}
        onSelectChat={selectChat}
        onNewChat={createNewChat}
      />
      
      <div className="flex-1 flex flex-col">
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
        />
        
        <MessageInput
          onSendMessage={sendMessage}
          disabled={isLoading}
        />
      </div>
    </div>
  );
}

export default App;
