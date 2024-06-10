import React, { useState, useEffect, useRef, useCallback } from 'react';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import apiService from '../services/apiService';
import './Layout.css';

const Layout = () => {
  const [chatSessions, setChatSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [offset, setOffset] = useState(0);
  const [searchText, setSearchText] = useState('');
  const isFetchingRef = useRef(false);
  const fetchedSessionIds = useRef(new Set());
  const limit = 20;

  const fetchChatSessions = useCallback(async (newOffset, searchText = '') => {
    isFetchingRef.current = true;
    try {
      const userInput = { limit, offset: newOffset, search_text: searchText };
      const response = await apiService.triggerDBRequest(
        "db",
        searchText ? "db_search_messages" : "db_all_sessions_for_user",
        userInput
      );
      const sessions = response.message.result;

      const uniqueSessions = sessions.filter(
        session => !fetchedSessionIds.current.has(session.session_id)
      );

      // Add the new session ids to the fetchedSessionIds set
      uniqueSessions.forEach(session => fetchedSessionIds.current.add(session.session_id));

      // Update the state with the unique sessions
      setChatSessions(prevSessions => (newOffset === 0 ? uniqueSessions : [...prevSessions, ...uniqueSessions]));
    } catch (error) {
      console.error('Failed to fetch chat sessions', error);
    }
    isFetchingRef.current = false;
  }, [limit]);

  const loadMoreSessions = useCallback(() => {
    if (!isFetchingRef.current) {
      const newOffset = offset + limit;
      setOffset(newOffset);
      //fetchChatSessions(newOffset);
    }
  }, [offset, limit]);
  //}, [offset, fetchChatSessions, limit]);

  const updateSessionName = (sessionId, newName) => {
    setChatSessions(prevSessions => prevSessions.map(session =>
      session.session_id === sessionId ? { ...session, session_name: newName } : session
    ));
  };

  const removeSession = (sessionId) => {
    setChatSessions(prevSessions => prevSessions.filter(session => session.session_id !== sessionId));
    if (selectedSession && selectedSession.session_id === sessionId) {
      setSelectedSession(null); // Clear the current session if it is removed
    }
  };

  useEffect(() => {
    if (isFetchingRef.current) return;
    fetchChatSessions(offset, searchText);
  }, [offset, fetchChatSessions, searchText]);

  const handleSearch = (term) => {
    setSearchText(term);
    setOffset(0);
    fetchedSessionIds.current.clear();
    setChatSessions([]);
  };

  return (
    <div className="layout">
      <Sidebar
        chatSessions={chatSessions}
        onSelectSession={setSelectedSession}
        loadMoreSessions={loadMoreSessions}
        updateSessionName={updateSessionName}
        removeSession={removeSession}
        onSearch={handleSearch}
      />
      <ChatWindow selectedSession={selectedSession} />
    </div>
  );
};

export default Layout;
