// Layout.js
import React, { useState, useEffect, useRef, useCallback } from 'react';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import apiService from '../services/apiService';
import './Layout.css';

const Layout = () => {
  const [chatSessions, setChatSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [offset, setOffset] = useState(0);
  const [isFetching, setIsFetching] = useState(false);
  const fetchedSessionIds = useRef(new Set());
  const limit = 5;

  const fetchChatSessions = async (newOffset) => {
    setIsFetching(true);
    console.log(`Fetching chat sessions with offset: ${newOffset}`);
    try {
      const userInput = { "limit": limit, "offset": newOffset };
      const response = await apiService.triggerDBRequest("db_all_sessions_for_user", userInput);
      const sessions = response.message.result;
      console.log('Fetched sessions:', sessions);

      // Filter out duplicate sessions
      const uniqueSessions = sessions.filter(
        session => !fetchedSessionIds.current.has(session.session_id)
      );
      console.log('Unique sessions to add:', uniqueSessions);

      // Add the new session ids to the fetchedSessionIds set
      uniqueSessions.forEach(session => fetchedSessionIds.current.add(session.session_id));
      
      // Update the state with the unique sessions
      setChatSessions(prevSessions => [...prevSessions, ...uniqueSessions]);
    } catch (error) {
      console.error('Failed to fetch chat sessions', error);
    }
    setIsFetching(false);
  };

  const loadMoreSessions = useCallback(() => {
    if (!isFetching) {
      const newOffset = offset + limit;
      console.log(`Loading more sessions, new offset: ${newOffset}`);
      setOffset(newOffset);
    }
  }, [isFetching, offset]);

  const updateSessionName = (sessionId, newName) => {
    setChatSessions(prevSessions => prevSessions.map(session =>
      session.session_id === sessionId ? { ...session, session_name: newName } : session
    ));
  };

  const removeSession = (sessionId) => {
    setChatSessions(prevSessions => prevSessions.filter(session => session.session_id !== sessionId));
  };

  useEffect(() => {
    fetchChatSessions(offset);
  }, [offset]);

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
