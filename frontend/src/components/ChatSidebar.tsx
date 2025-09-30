import React from 'react';
import { format } from 'date-fns';
import { MessageCircle, Plus } from 'lucide-react';

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

interface ChatSidebarProps {
  chatHistory: ChatHistory[];
  currentChatId?: string;
  onSelectChat: (chatId: string) => void;
  onNewChat: () => void;
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({
  chatHistory,
  currentChatId,
  onSelectChat,
  onNewChat,
}) => {
  return (
    <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Chat History</h2>
          <button
            onClick={onNewChat}
            className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            title="New Chat"
          >
            <Plus size={16} />
          </button>
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto p-2">
        {chatHistory.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <MessageCircle size={48} className="mx-auto mb-2 opacity-50" />
            <p>No chat history yet</p>
            <p className="text-sm">Start a conversation!</p>
          </div>
        ) : (
          <div className="space-y-2">
            {chatHistory.map((chat) => (
              <div
                key={chat.id}
                onClick={() => onSelectChat(chat.id)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  currentChatId === chat.id
                    ? 'bg-blue-100 border-2 border-blue-300'
                    : 'bg-white border border-gray-200 hover:bg-gray-50'
                }`}
              >
                <h3 className="font-medium text-gray-900 truncate mb-1">
                  {chat.title}
                </h3>
                <p className="text-sm text-gray-600 truncate mb-2">
                  {chat.lastMessage}
                </p>
                <p className="text-xs text-gray-400">
                  {format(new Date(chat.timestamp), 'MMM d, HH:mm')}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-center text-sm text-gray-500">
          ServiceNow Chatbot
        </div>
      </div>
    </div>
  );
};