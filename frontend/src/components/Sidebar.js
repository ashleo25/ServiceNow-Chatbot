import React, { useState } from 'react';
import { Plus, MessageSquare, Trash2, Clock } from 'lucide-react';
import './Sidebar.css';

const Sidebar = ({ 
  chats = [],
  currentChatId, 
  onNewChat, 
  onSelectChat, 
  onDeleteChat, 
  isSidebarOpen,
  toggleSidebar,
  onUpdateChatTitle
}) => {
  const [hoveredChatId, setHoveredChatId] = useState(null);

  const addNewChat = () => {
    onNewChat();
  };

  const deleteChat = (chatId, e) => {
    e.stopPropagation();
    if (onDeleteChat) {
      onDeleteChat(chatId);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 168) { // 7 days
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  const truncateText = (text, maxLength = 50) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div className={`sidebar ${!isSidebarOpen ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <button 
          className="new-chat-button"
          onClick={addNewChat}
          title="New Chat"
        >
          <Plus size={20} />
          {isSidebarOpen && <span>New Chat</span>}
        </button>
        
        <button 
          className="collapse-button"
          onClick={toggleSidebar}
          title={!isSidebarOpen ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          <MessageSquare size={18} />
        </button>
      </div>

      <div className="sidebar-content">
        <div className="chat-history">
          <h3 className="history-title">
            {isSidebarOpen && 'Recent Chats'}
          </h3>
          
          <div className="chat-list">
            {chats.length === 0 ? (
              <div className="empty-state">
                <MessageSquare size={32} />
                <p>No chat history yet</p>
                <span>Start a new conversation!</span>
              </div>
            ) : (
              chats.map((chat) => (
                <div
                  key={chat.id}
                  className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
                  onClick={() => onSelectChat(chat.id)}
                  onMouseEnter={() => setHoveredChatId(chat.id)}
                  onMouseLeave={() => setHoveredChatId(null)}
                  data-title={truncateText(chat.title, 30)}
                >
                  <div className="chat-content">
                    <div className="chat-title">
                      {truncateText(chat.title)}
                    </div>
                    <div className="chat-preview">
                      {chat.messages && chat.messages.length > 0 
                        ? truncateText(chat.messages[chat.messages.length - 1].content)
                        : 'Start a new conversation...'
                      }
                    </div>
                    <div className="chat-meta">
                      <span className="chat-time">
                        <Clock size={12} />
                        {formatTimestamp(chat.timestamp)}
                      </span>
                      {chat.messages && chat.messages.length > 0 && (
                        <span className="message-count">
                          {chat.messages.length} messages
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {hoveredChatId === chat.id && (
                    <button
                      className="delete-chat-button"
                      onClick={(e) => deleteChat(chat.id, e)}
                      title="Delete Chat"
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="footer-info">
          <div className="footer-icon">
            <MessageSquare size={16} />
          </div>
          {isSidebarOpen && (
            <div className="footer-text">
              <span>IT Support Assistant</span>
              <span>Powered by AI</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;