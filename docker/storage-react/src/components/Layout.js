// Layout.js
import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import apiService from '../services/apiService';
import './Layout.css'; // Assuming you have CSS for layout

const Layout = () => {
  const [chatSessions, setChatSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);

  useEffect(() => {
    // Fetch chat sessions when component mounts
    const fetchChatSessions = async () => {
      try {
        const sessions = await apiService.fetchChatSessions();
        console.log("Fetched chat sessions:", sessions);
        setChatSessions(Array.isArray(sessions) ? sessions : []);
      } catch (error) {
        console.error('Failed to fetch chat sessions', error);
      }
    };

    fetchChatSessions();
  }, []);

  return (
    <div className="layout">
      <Sidebar
        chatSessions={chatSessions}
        onSelectSession={setSelectedSession}
      />
      <ChatWindow selectedSession={selectedSession} />
    </div>
  );
};

export default Layout;
