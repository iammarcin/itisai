// Sidebar.js
import React, { useState, useEffect, useRef } from 'react';
import './Sidebar.css';

const Sidebar = ({ chatSessions, onSelectSession, loadMoreSessions }) => {
  const [contextMenu, setContextMenu] = useState(null);
  const observer = useRef();

  useEffect(() => {
    if (observer.current) observer.current.disconnect();

    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) {
        loadMoreSessions();
      }
    });

    if (observer.current) {
      const loadMoreElement = document.querySelector('.load-more');
      if (loadMoreElement) {
        observer.current.observe(loadMoreElement);
      }
    }

    return () => observer.current && observer.current.disconnect();
  }, [chatSessions, loadMoreSessions]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}`;
  };

  const handleRightClick = (event, session) => {
    event.preventDefault();
    setContextMenu({
      x: event.pageX,
      y: event.pageY,
      session
    });
  };

  const handleRename = () => {
    console.log('Rename', contextMenu.session);
    setContextMenu(null);
  };

  const handleRemove = () => {
    console.log('Remove', contextMenu.session);
    setContextMenu(null);
  };

  return (
    <div className="sidebar">
      <h2>Chat Sessions</h2>
      <ul>
        {chatSessions.map((session) => (
          <li
            key={session.session_id}
            onClick={() => onSelectSession(session)}
            onContextMenu={(e) => handleRightClick(e, session)}
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
    </div>
  );
};

export default Sidebar;
