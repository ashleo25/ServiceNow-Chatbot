import React, { useState, useEffect, useRef, useCallback } from 'react';
import { chatAPI } from '../services/api';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import LoadingSpinner from './LoadingSpinner';
import { useToast } from './Toast';
import './EnhancedChatInterface.css';

const EnhancedChatInterface = ({
  isConnected,
  currentChat,
  setChats,
  setCurrentChatId,
  handleNewChat
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const toast = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addMessageToChat = useCallback((chatId, sender, content, metadata = {}) => {
    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === chatId
          ? {
              ...chat,
              messages: [
                ...chat.messages,
                {
                  id: Date.now() + Math.random(),
                  sender,
                  content,
                  timestamp: new Date().toISOString(),
                  ...metadata,
                },
              ],
            }
          : chat
      )
    );
  }, [setChats]);

  const updateChatSessionData = useCallback((chatId, newSessionData) => {
    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === chatId
          ? { ...chat, sessionData: newSessionData }
          : chat
      )
    );
  }, [setChats]);

  const updateChatTitle = useCallback((chatId, firstUserMessage) => {
    if (!firstUserMessage || firstUserMessage.trim().length === 0) return;
    
    // Generate a better title based on the first user message
    let title = firstUserMessage.trim();
    
    // If it's a question, remove the question mark for cleaner title
    if (title.endsWith('?')) {
      title = title.slice(0, -1);
    }
    
    // If it's too long, truncate intelligently at word boundary
    if (title.length > 50) {
      const truncated = title.substring(0, 47);
      const lastSpace = truncated.lastIndexOf(' ');
      if (lastSpace > 20) {
        title = truncated.substring(0, lastSpace) + '...';
      } else {
        title = truncated + '...';
      }
    }
    
    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === chatId && chat.title === 'New Chat'
          ? { ...chat, title: title }
          : chat
      )
    );
  }, [setChats]);

  const handleSendMessage = useCallback(async (message, isInitial = false) => {
    if (!isConnected) {
      addMessageToChat(currentChat.id, 'system', 'Backend not connected. Please check your connection.');
      toast.error('Backend connection lost. Please check your connection and try again.');
      return;
    }

    if (!message.trim() && !isInitial) return;

    setIsLoading(true);

    if (!isInitial) {
      addMessageToChat(currentChat.id, 'user', message);
      if (currentChat.title === 'New Chat') {
        updateChatTitle(currentChat.id, message);
      }
    }

    try {
      const response = await chatAPI.sendEnhancedMessage(message, currentChat.sessionData);
      
      if (response.session_data) {
        updateChatSessionData(currentChat.id, response.session_data);
      }

      // Handle different message types including ticket creation
      const messageMetadata = {
        messageType: response.message_type,
        nextAction: response.next_action,
        searchResults: response.search_results,
        ticketResult: response.ticket_result,
        duplicates: response.duplicates,
        requiresUserDecision: response.requires_user_decision
      };

      addMessageToChat(currentChat.id, 'bot', response.response, messageMetadata);

      // Show success toast for ticket creation
      if (response.ticket_result?.success) {
        toast.success(`Ticket ${response.ticket_result.ticket_number} created successfully!`, {
          title: 'Ticket Created'
        });
      }

    } catch (error) {
      const errorMessage = `Error: ${error.message}`;
      addMessageToChat(currentChat.id, 'system', errorMessage);
      toast.error(errorMessage, {
        title: 'Request Failed'
      });
    } finally {
      setIsLoading(false);
    }
  }, [isConnected, currentChat, addMessageToChat, updateChatSessionData, updateChatTitle, toast]);

  // Effect to scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [currentChat?.messages]);

  // Effect to send initial welcome message if chat is new and empty
  useEffect(() => {
    if (isConnected && currentChat && currentChat.messages.length === 0) {
      const welcomeMessage = `# Welcome to IT Support Assistant! 👋

I'm your dedicated IT Support Assistant, here to help you with a wide range of IT-related queries and issues.

## What I can help you with:

- **Incident Management**: Report problems with your IT services
- **Service Requests**: Request new IT services or equipment  
- **Change Management**: Inquire about planned IT changes
- **Problem Management**: Report recurring issues or seek solutions
- **Status Updates**: Check the status of your existing tickets
- **Knowledge Base**: Find information and solutions from our knowledge base

I'll first search our knowledge base and existing tickets to help you find solutions. If that doesn't help, I can create a formal ticket for you.

**How can I assist you today?**`;
      
      addMessageToChat(currentChat.id, 'bot', welcomeMessage, { 
        messageType: 'welcome' 
      });
    }
  }, [isConnected, currentChat, addMessageToChat]);

  // Effect to handle custom events from MessageList
  useEffect(() => {
    const handleCreateTicket = () => {
      handleSendMessage('create ticket');
    };

    const handleNewSearch = () => {
      handleSendMessage('new search');
    };

    window.addEventListener('createTicket', handleCreateTicket);
    window.addEventListener('newSearch', handleNewSearch);

    return () => {
      window.removeEventListener('createTicket', handleCreateTicket);
      window.removeEventListener('newSearch', handleNewSearch);
    };
  }, [handleSendMessage]);

  const handleReset = () => {
    handleNewChat();
  };

  return (
    <div className="enhanced-chat-interface">
      <div className="chat-messages">
        <MessageList 
          messages={currentChat?.messages || []} 
          isLoading={isLoading}
          isEnhanced={true}
        />
        {isLoading && (
          <div className="typing-indicator">
            <LoadingSpinner 
              size="small" 
              color="secondary" 
              text="AI is thinking..." 
              className="typing-indicator"
            />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={!isConnected || isLoading}
          placeholder={
            isLoading ? "AI is processing your message..." :
            currentChat?.sessionData?.conversation_stage === 'data_collection' 
              ? "Please provide the requested information..."
              : "Message IT Support Assistant..."
          }
        />
      </div>
    </div>
  );
};

export default EnhancedChatInterface;