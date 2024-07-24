// Sidebar.js

import React, { useState, useEffect, useRef, useCallback, useContext } from 'react';

import { StateContext } from './StateContextProvider';

import './css/Sidebar.css';
import apiMethods from '../services/api.methods';
import useDebounce from '../hooks/useDebounce';
import { formatDate } from '../utils/misc';

const Sidebar = ({ onSelectSession }) => {
  const [chatSessions, setChatSessions] = useState([]);
  const [offset, setOffset] = useState(0);
  const limit = 20;
  const [searchText, setSearchText] = useState('');
  const [isSearchMode, setIsSearchMode] = useState(false);
  const [hasMoreSessions, setHasMoreSessions] = useState(true);
  const isFetchingRef = useRef(false);
  const fetchedSessionIds = useRef(new Set());
  const debouncedSearchText = useDebounce(searchText, 500);
  const observer = useRef();
  const [contextMenu, setContextMenu] = useState(null);
  const [renamePopup, setRenamePopup] = useState(null);
  const renameInputRef = useRef(null);

  const {
    chatContent, currentSessionIndex,
    currentSessionId, setCurrentSessionId,
    refreshChatSessions, setRefreshChatSessions,
    setErrorMsg
  } = useContext(StateContext);

  // get the list of user's sessions (for general first load and search mode)
  const fetchChatSessions = useCallback(async (newOffset, searchText = '') => {
    isFetchingRef.current = true;
    try {
      const userInput = { limit, offset: newOffset, search_text: searchText };
      const response = await apiMethods.triggerAPIRequest(
        "api/db",
        "provider.db",
        searchText ? "db_search_messages" : "db_all_sessions_for_user",
        userInput
      );

      const sessions = response.message.result;

      const uniqueSessions = sessions.filter(
        session => !fetchedSessionIds.current.has(session.session_id)
      );

      uniqueSessions.forEach(session => fetchedSessionIds.current.add(session.session_id));

      setChatSessions(prevSessions => (newOffset === 0 ? uniqueSessions : [...prevSessions, ...uniqueSessions]));
      setRefreshChatSessions(false);
      // Check if we received fewer sessions than the limit, indicating no more sessions are available
      if (sessions.length < limit) {
        setHasMoreSessions(false);
      } else {
        setHasMoreSessions(true);
      }
    } catch (error) {
      setErrorMsg("Problem with fetching data. Try again.");
      console.error('Failed to fetch chat sessions', error);
    }
    isFetchingRef.current = false;
  }, [limit, setErrorMsg, setRefreshChatSessions]);

  // load more sessions when user scrolls down
  const loadMoreSessions = useCallback(() => {
    if (!isFetchingRef.current && !isSearchMode && hasMoreSessions) {
      const newOffset = offset + limit;
      setOffset(newOffset);
    }
    // and this is when we clear search text in search bar
    if (!isFetchingRef.current && !isSearchMode && hasMoreSessions && fetchedSessionIds.current.size === 0) {
      setOffset(0)
    }
  }, [offset, limit, isSearchMode, hasMoreSessions]);

  const removeSession = (sessionId) => {
    setChatSessions(prevSessions => prevSessions.filter(session => session.session_id !== sessionId));
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null);
    }
  };

  // making sure that we fetch the list of sessions properly (only once)
  useEffect(() => {
    if (isFetchingRef.current) return;
    fetchChatSessions(offset, debouncedSearchText);
  }, [offset, fetchChatSessions, debouncedSearchText]);

  // if refreshChatSessions is set in initial few messages (via ChatHandleAPI) - we want to refresh list of sessions (so new one appears)
  useEffect(() => {
    if (refreshChatSessions) {
      handleSearch("");
      setOffset(0);
      fetchChatSessions(0, debouncedSearchText);
    }
  }, [refreshChatSessions, debouncedSearchText, fetchChatSessions]);

  const handleSearch = (term) => {
    setSearchText(term);
    setOffset(0);
    fetchedSessionIds.current.clear();
    setChatSessions([]);
    setIsSearchMode(term !== '');
    setHasMoreSessions(true); // Reset hasMoreSessions on new search
  };

  const handleSearchInputChange = (event) => {
    handleSearch(event.target.value);
  };

  // observer watching if user scrolls down till end of the sidebar with list of chats
  // if it goes down - new sessions are loaded
  useEffect(() => {
    if (observer.current) observer.current.disconnect();

    if (!isSearchMode && hasMoreSessions) {
      observer.current = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting) {
          loadMoreSessions();
        }
      });

      const loadMoreElement = document.querySelector('.load-more');
      if (loadMoreElement) {
        observer.current.observe(loadMoreElement);
      }
    }

    return () => observer.current && observer.current.disconnect();
  }, [chatSessions, loadMoreSessions, isSearchMode, hasMoreSessions]);

  // put focus on input so user can start typing
  useEffect(() => {
    if (renamePopup) {
      renameInputRef.current.focus();
    }
  }, [renamePopup]);

  // show context menu when right click is detected
  const handleRightClick = (event, session) => {
    event.preventDefault();
    setContextMenu({
      x: event.pageX,
      y: event.pageY,
      session
    });
  };

  // and listener for click outside (if context menu appears and we click somewhere else we want to hide it)
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (contextMenu && !event.target.closest('.context-menu')) {
        setContextMenu(null);
      }
    };

    if (contextMenu) {
      document.addEventListener('click', handleClickOutside);
    } else {
      document.removeEventListener('click', handleClickOutside);
    }

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [contextMenu]);

  const handleRename = () => {
    setRenamePopup({
      session: contextMenu.session,
      name: contextMenu.session.session_name
    });
    setContextMenu(null);
  };

  const handleRemove = async () => {
    try {
      const userInput = { "session_id": contextMenu.session.session_id };
      await apiMethods.triggerAPIRequest("api/db", "provider.db", "db_remove_session", userInput);
      removeSession(contextMenu.session.session_id);
    } catch (error) {
      console.error('Failed to remove session', error);
    }
    setContextMenu(null);
  };

  const handleRenameChange = (event) => {
    setRenamePopup({
      ...renamePopup,
      name: event.target.value
    });
  };

  const handleRenameSubmit = (sessionId, newSessionName) => {
    const triggerDBRename = async () => {
      try {
        const currentSessionId = sessionId || renamePopup.session.session_id;
        const currentNewName = newSessionName || renamePopup.name;

        const userInput = {
          "session_id": currentSessionId,
          "new_session_name": currentNewName
        };
        await apiMethods.triggerAPIRequest("api/db", "provider.db", "db_update_session", userInput);

        setChatSessions(prevSessions => prevSessions.map(session =>
          session.session_id === currentSessionId ? { ...session, session_name: currentNewName } : session
        ));
      } catch (error) {
        console.error('Failed to rename session', error);
      }
    }
    triggerDBRename();
    setRenamePopup(null);
  };

  const handleAutoRename = async () => {
    setContextMenu(null);
    try {
      const firstTwoMessages = chatContent[currentSessionIndex].messages.slice(0, 2);
      const firstTwoMessagesContent = `request: ${firstTwoMessages[0].message}\nresponse: ${firstTwoMessages[1].message}`;
      const userInput = { "text": firstTwoMessagesContent };
      const response = await apiMethods.triggerAPIRequest("generate", "text", "generate_session_name", userInput);
      if (response.success) {
        const newSessionName = response.message.result;
        handleRenameSubmit(contextMenu.session.session_id, newSessionName);
      }
    } catch (error) {
      console.error('Failed to rename session', error);
    }

  };


  const handleRenameCancel = () => {
    setRenamePopup(null);
  };

  // when any session chosen we trigger handleSelectSession from Main
  const handleSelectSession = (session) => {
    onSelectSession(session);

  };

  // for pressing Enter or Escape we want to submit or cancel renaming
  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleRenameSubmit();
    } else if (event.key === 'Escape') {
      handleRenameCancel();
    }
  };

  return (
    <div className="sidebar">
      <input
        type="text"
        className="search-bar"
        placeholder="Search sessions..."
        onChange={handleSearchInputChange}
      />
      <ul>
        {chatSessions.map((session) => (
          <li
            key={session.session_id}
            onClick={() => handleSelectSession(session)}
            onContextMenu={(e) => handleRightClick(e, session)}
            className={currentSessionId === session.session_id ? 'selected' : ''}
          >
            <div className="session-item">
              <img
                src={`/imgs/${session.ai_character_name}.png`}
                alt={session.ai_character_name}
                className="avatar"
              />
              <div className="session-details">
                <div className="session-name">{session.session_name}</div>
                <div className="session-date">{formatDate(session.last_update)}</div>
              </div>
            </div>
          </li>
        ))}
        <div className="load-more"></div>
      </ul>
      {contextMenu && (
        <div
          className="context-menu"
          style={{ top: contextMenu.y, left: contextMenu.x }}
        >
          <div className="context-menu-item" onClick={handleRename}>Rename</div>
          <div className="context-menu-item" onClick={handleAutoRename}>Auto rename</div>
          <div className="context-menu-item" onClick={handleRemove}>Remove</div>
        </div>
      )}
      {renamePopup && (
        <div className="rename-popup">
          <div className="rename-popup-content">
            <h3>Rename Session</h3>
            <input
              type="text"
              value={renamePopup.name}
              onChange={handleRenameChange}
              onKeyDown={handleKeyDown}
              ref={renameInputRef}
            />
            <div className="button-group">
              <button onClick={handleRenameSubmit}>Submit</button>
              <button onClick={handleRenameCancel}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
