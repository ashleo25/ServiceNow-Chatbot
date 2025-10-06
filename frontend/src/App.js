import React, { useState, useEffect, useCallback } from 'react';
import EnhancedChatInterface from './components/EnhancedChatInterface';
import Sidebar from './components/Sidebar';
import ThemeToggle from './components/ThemeToggle';
import { ToastProvider } from './components/Toast';
import { ChatProvider } from './context/ChatContext';
import { ThemeProvider } from './hooks/useTheme';
import './styles/globals.css';
import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const checkConnection = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const data = await response.json();
      const connected = data.status === 'healthy' && data.search_agent_initialized;
      setIsConnected(connected);
    } catch (error) {
      setIsConnected(false);
    }
  }, []);

  useEffect(() => {
    setTimeout(checkConnection, 1000);
    const interval = setInterval(checkConnection, 10000);
    return () => clearInterval(interval);
  }, [checkConnection]);

  // Load chats from localStorage on initial render
  useEffect(() => {
    const savedChats = JSON.parse(localStorage.getItem('chats')) || [];
    setChats(savedChats);
    if (savedChats.length > 0) {
      setCurrentChatId(savedChats[0].id);
    } else {
      handleNewChat();
    }
  }, []);

  // Save chats to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('chats', JSON.stringify(chats));
  }, [chats]);

  const handleNewChat = useCallback(() => {
    const newChat = {
      id: Date.now(),
      title: 'New Chat',
      messages: [],
      timestamp: new Date().toISOString(),
      sessionData: null,
    };
    setChats(prevChats => [newChat, ...prevChats]);
    setCurrentChatId(newChat.id);
    setIsSidebarOpen(false);
  }, []);

  const handleSelectChat = useCallback((chatId) => {
    setCurrentChatId(chatId);
    setIsSidebarOpen(false);
  }, []);

  const handleDeleteChat = useCallback((chatIdToDelete) => {
    if (window.confirm('Are you sure you want to delete this chat?')) {
      setChats(prevChats => {
        const updatedChats = prevChats.filter(chat => chat.id !== chatIdToDelete);
        if (currentChatId === chatIdToDelete) {
          if (updatedChats.length > 0) {
            setCurrentChatId(updatedChats[0].id);
          } else {
            handleNewChat();
          }
        }
        return updatedChats;
      });
    }
  }, [currentChatId, handleNewChat]);

  const handleUpdateChatTitle = useCallback((chatId, newTitle) => {
    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === chatId ? { ...chat, title: newTitle } : chat
      )
    );
  }, []);

  const toggleSidebar = useCallback(() => {
    setIsSidebarOpen(prev => !prev);
  }, []);

  const currentChat = chats.find(chat => chat.id === currentChatId);

  return (
    <ThemeProvider defaultTheme="light">
      <ToastProvider>
        <ChatProvider>
          <div className="app">
            <Sidebar
              chats={chats}
              onSelectChat={handleSelectChat}
              onNewChat={handleNewChat}
              onDeleteChat={handleDeleteChat}
              currentChatId={currentChatId}
              isSidebarOpen={isSidebarOpen}
              toggleSidebar={toggleSidebar}
              onUpdateChatTitle={handleUpdateChatTitle}
            />
            <div className={`main-content ${isSidebarOpen ? 'sidebar-open' : ''}`}>
              {/* Theme Toggle - positioned absolutely */}
              <div className="theme-toggle-wrapper">
                <ThemeToggle className="compact" />
              </div>
              
              {currentChat ? (
                <EnhancedChatInterface
                  isConnected={isConnected}
                  currentChat={currentChat}
                  setChats={setChats}
                  setCurrentChatId={setCurrentChatId}
                  handleNewChat={handleNewChat}
                />
              ) : (
                <div className="no-chat-selected">
                  <p>Select a chat from the sidebar or start a new one.</p>
                  <button onClick={handleNewChat} className="new-chat-button-main">Start New Chat</button>
                </div>
              )}
            </div>
          </div>
        </ChatProvider>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;