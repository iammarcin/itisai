import React from 'react';
import './css/BottomToolsMenu.css';

const BottomToolsMenu = () => {
 return (
  <div className="bottom-tools-menu">
   <input type="text" className="message-input" placeholder="Message" />
   <button className="record-button">🎤</button>
   <button className="attach-button">📎</button>
  </div>
 );
};

export default BottomToolsMenu;
