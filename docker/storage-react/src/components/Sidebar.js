// Sidebar.js
import { useEffect } from 'react';
import React from 'react';
import './Sidebar.css'; // Assuming you have CSS for sidebar

const Sidebar = ({ chatSessions, onSelectSession }) => {
  console.log("Sidebar chatSessions:", chatSessions);



  if (!Array.isArray(chatSessions) || chatSessions.length === 0) {
    return <div className="sidebar">No chat sessions available</div>;
  }

  return (
    <div className="sidebar">
      <h2>Chat Sessions</h2>
      <ul>
        {chatSessions.map((session) => (
          <li
            key={session.session_id}
            onClick={() => onSelectSession(session)}
          >
            {session.session_name}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;
