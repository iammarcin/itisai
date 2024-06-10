import React, { useState, useEffect, useRef } from 'react';
import './Sidebar.css';
import apiService from '../services/apiService';

const Sidebar = ({ chatSessions, onSelectSession, loadMoreSessions, updateSessionName, removeSession, onSearch, isSearchMode }) => {
  const [contextMenu, setContextMenu] = useState(null);
  const [renamePopup, setRenamePopup] = useState(null);
  const observer = useRef();
  const [selectedSessionId, setSelectedSessionId] = useState(null);
  const renameInputRef = useRef(null);

  const handleSearchInputChange = (event) => {
    onSearch(event.target.value);
  };

  useEffect(() => {
    if (observer.current) observer.current.disconnect();

    if (!isSearchMode) {
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
  }, [chatSessions, loadMoreSessions, isSearchMode]);

  useEffect(() => {
    if (renamePopup) {
      renameInputRef.current.focus();
    }
  }, [renamePopup]);

  const handleRightClick = (event, session) => {
    event.preventDefault();
    setContextMenu({
      x: event.pageX,
      y: event.pageY,
      session
    });
  };

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
      await apiService.triggerDBRequest("db", "db_remove_session", userInput);
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

  const handleRenameSubmit = () => {
    const triggerDBRename = async () => {
      try {
        const userInput = { "session_id": renamePopup.session.session_id, "new_session_name": renamePopup.name };
        await apiService.triggerDBRequest("db", "db_update_session", userInput);
        updateSessionName(renamePopup.session.session_id, renamePopup.name);
      } catch (error) {
        console.error('Failed to rename session', error);
      }
    }
    triggerDBRename();
    setRenamePopup(null);
  };

  const handleRenameCancel = () => {
    setRenamePopup(null);
  };

  const handleSelectSession = (session) => {
    setSelectedSessionId(session.session_id);
    onSelectSession(session);
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleRenameSubmit();
    } else if (event.key === 'Escape') {
      handleRenameCancel();
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
  };

  return (
    <div className="sidebar">
      <h2>Chat Sessions</h2>
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
            className={selectedSessionId === session.session_id ? 'selected' : ''}
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
