import React, { useState } from 'react';
import './css/TopMenu.css';
import { getEnvironment, setEnvironment } from '../utils/local.storage';

const TopMenu = () => {
 const [environment, setLocalEnvironment] = useState(getEnvironment());
 // to display dropdown menu with environments only in non-production mode
 const isProduction = process.env.NODE_ENV === 'production';

 const handleEnvironmentChange = (event) => {
  const selectedEnv = event.target.value;
  setLocalEnvironment(selectedEnv);
  setEnvironment(selectedEnv);
  window.location.reload(); // Reload to apply the new environment
 };

 return (
  <div className="top-menu">
   <button className="menu-button">
    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M120-240v-80h720v80H120Zm0-200v-80h720v80H120Zm0-200v-80h720v80H120Z" /></svg>
   </button>

   {!isProduction ?
    <div className="environment-selector">
     <select id="environment" value={environment} onChange={handleEnvironmentChange}>
      <option value="prod">Prod</option>
      <option value="nonprod">Nonprod</option>
     </select>
    </div>
    : null}
   <button className="new-chat-button">
    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h280v80H200v560h560v-280h80v280q0 33-23.5 56.5T760-120H200Zm188-212-56-56 372-372H560v-80h280v280h-80v-144L388-332Z" /></svg>
   </button>
  </div>
 );
};

export default TopMenu;
