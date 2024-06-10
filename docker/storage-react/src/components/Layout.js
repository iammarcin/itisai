import React, { useState, useEffect, useRef, useCallback } from 'react';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import apiService from '../services/apiService';
import './Layout.css';

const Layout = () => {
  const [chatSessions, setChatSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [offset, setOffset] = useState(0);
  const isFetchingRef = useRef(false);
  const fetchedSessionIds = useRef(new Set());
  const limit = 20;

  const fetchChatSessions = useCallback(async (newOffset) => {
    isFetchingRef.current = true;
    try {
      const userInput = { "limit": limit, "offset": newOffset };
      const response = await apiService.triggerDBRequest("db", "db_all_sessions_for_user", userInput);
      const sessions = response.message.result;

      const uniqueSessions = sessions.filter(
        session => !fetchedSessionIds.current.has(session.session_id)
      );

      uniqueSessions.forEach(session => fetchedSessionIds.current.add(session.session_id));

      setChatSessions(prevSessions => [...prevSessions, ...uniqueSessions]);
    } catch (error) {
      console.error('Failed to fetch chat sessions', error);
    }
    isFetchingRef.current = false;
  }, [limit]);

  const loadMoreSessions = useCallback(() => {
    if (!isFetchingRef.current) {
      const newOffset = offset + limit;
      setOffset(newOffset);
      fetchChatSessions(newOffset);
    }
  }, [offset, fetchChatSessions, limit]);

  const updateSessionName = (sessionId, newName) => {
    setChatSessions(prevSessions => prevSessions.map(session =>
      session.session_id === sessionId ? { ...session, session_name: newName } : session
    ));
  };

  const removeSession = (sessionId) => {
    setChatSessions(prevSessions => prevSessions.filter(session => session.session_id !== sessionId));
    if (selectedSession && selectedSession.session_id === sessionId) {
      setSelectedSession(null);
    }
  };

  useEffect(() => {
    if (isFetchingRef.current) return;
    fetchChatSessions(0); // Initial fetch
  }, [fetchChatSessions]);

  return (
    <div className="layout">
      <Sidebar
        chatSessions={chatSessions}
        onSelectSession={setSelectedSession}
        loadMoreSessions={loadMoreSessions}
        updateSessionName={updateSessionName}
        removeSession={removeSession}
      />
      <ChatWindow selectedSession={selectedSession} />
    </div>
  );
};

export default Layout;
