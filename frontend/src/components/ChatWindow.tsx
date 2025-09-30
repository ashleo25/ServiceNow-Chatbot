import React, { useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';

interface Message {
  id: string;
  message: string;
  timestamp: string;
  is_user: boolean;
}

interface ChatWindowProps {
  messages: Message[];
  isLoading?: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="text-6xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              ServiceNow Assistant
            </h3>
            <p className="text-gray-500 max-w-md">
              Hi! I'm here to help you with ServiceNow tickets. I can:
            </p>
            <ul className="text-gray-500 text-left mt-4 space-y-2">
              <li>• Check for duplicate tickets</li>
              <li>• Search for similar issues and solutions</li>
              <li>• Link you to existing tickets</li>
              <li>• Create new incidents when needed</li>
            </ul>
            <p className="text-gray-500 mt-4">
              Just describe your issue and I'll get started!
            </p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-gray-100 border rounded-lg px-4 py-2">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm text-gray-500">Assistant is typing...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
};