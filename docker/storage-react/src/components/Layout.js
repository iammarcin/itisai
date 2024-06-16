// Layout.js

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import apiMethods from '../services/api.methods';
import './css/Layout.css';
import useDebounce from '../hooks/useDebounce';

const Layout = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [chatSessions, setChatSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [offset, setOffset] = useState(0);
  const [searchText, setSearchText] = useState('');
  const [isSearchMode, setIsSearchMode] = useState(false);
  const [hasMoreSessions, setHasMoreSessions] = useState(true); // New state
  const isFetchingRef = useRef(false);
  const fetchedSessionIds = useRef(new Set());
  const limit = 20;

  // debounce hook (to prevent too many API calls)
  const debouncedSearchText = useDebounce(searchText, 500);

  const fetchChatSessions = useCallback(async (newOffset, searchText = '') => {
    isFetchingRef.current = true;
    try {
      const userInput = { limit, offset: newOffset, search_text: searchText };
      const response = await apiMethods.triggerDBRequest(
        "db",
        searchText ? "db_search_messages" : "db_all_sessions_for_user",
        userInput
      );
      const sessions = response.message.result;

      const uniqueSessions = sessions.filter(
        session => !fetchedSessionIds.current.has(session.session_id)
      );

      uniqueSessions.forEach(session => fetchedSessionIds.current.add(session.session_id));

      setChatSessions(prevSessions => (newOffset === 0 ? uniqueSessions : [...prevSessions, ...uniqueSessions]));

      // Check if we received fewer sessions than the limit, indicating no more sessions are available
      if (sessions.length < limit) {
        setHasMoreSessions(false);
      } else {
        setHasMoreSessions(true);
      }
    } catch (error) {
      console.error('Failed to fetch chat sessions', error);
    }
    isFetchingRef.current = false;
  }, [limit]);

  const loadMoreSessions = useCallback(() => {
    if (!isFetchingRef.current && !isSearchMode && hasMoreSessions) { // Check hasMoreSessions
      const newOffset = offset + limit;
      setOffset(newOffset);
    }
  }, [offset, limit, isSearchMode, hasMoreSessions]); // Add hasMoreSessions

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
    fetchChatSessions(offset, debouncedSearchText); // Use debounced search text
  }, [offset, fetchChatSessions, debouncedSearchText]);

  const handleSelectSession = (session) => {
    navigate(`/session/${session.session_id}`);
    setSelectedSession(session);
  };

  useEffect(() => {
    if (sessionId) {
      const selected = chatSessions.find(session => session.session_id === sessionId);
      setSelectedSession(selected);
    }
  }, [sessionId, chatSessions]);

  const handleSearch = (term) => {
    setSearchText(term);
    setOffset(0);
    fetchedSessionIds.current.clear();
    setChatSessions([]);
    setIsSearchMode(term !== '');
    setHasMoreSessions(true); // Reset hasMoreSessions on new search
  };

  return (
    <div className="layout">
      <Sidebar
        chatSessions={chatSessions}
        onSelectSession={handleSelectSession}
        loadMoreSessions={loadMoreSessions}
        updateSessionName={updateSessionName}
        removeSession={removeSession}
        onSearch={handleSearch}
        isSearchMode={isSearchMode}
        hasMoreSessions={hasMoreSessions} // Pass hasMoreSessions
      />
      <ChatWindow selectedSession={selectedSession} />
    </div>
  );
};

export default Layout;
