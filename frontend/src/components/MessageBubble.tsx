import React from 'react';
import { format } from 'date-fns';

interface Message {
  id: string;
  message: string;
  timestamp: string;
  is_user: boolean;
}

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const timestamp = new Date(message.timestamp);
  
  return (
    <div className={`flex ${message.is_user ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-2 ${
          message.is_user
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 text-gray-900 border'
        }`}
      >
        <div className="whitespace-pre-wrap">{message.message}</div>
        <div
          className={`text-xs mt-1 ${
            message.is_user ? 'text-blue-100' : 'text-gray-500'
          }`}
        >
          {format(timestamp, 'HH:mm')}
        </div>
      </div>
    </div>
  );
};