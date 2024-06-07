// Sidebar.js
import React from 'react';
import './Sidebar.css'; // Assuming you have CSS for sidebar

const Sidebar = ({ chatSessions, onSelectSession }) => {
  console.log("Sidebar chatSessions:", chatSessions);

  if (!Array.isArray(chatSessions) || chatSessions.length === 0) {
    return <div className="sidebar">No chat sessions available</div>;
  }

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
      <ul>
        {chatSessions.map((session) => (
          <li
            key={session.session_id}
            onClick={() => onSelectSession(session)}
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
      </ul>
    </div>
  );
};

export default Sidebar;
