// TopMenu.js

import React, { useState, useEffect } from 'react';
import './css/TopMenu.css';
import { getIsProdMode, setIsProdMode, setURLForAPICalls, getTextModelName } from '../utils/local.storage';
import OptionsWindow from './OptionsWindow';

const TopMenu = () => {
 const [isPopupVisible, setPopupVisible] = useState(false);
 const [isDropdownVisible, setDropdownVisible] = useState(false);
 // this is to track if we want to use prod or non prod backend (and will be only available in non prod react)
 const [environment, setEnvironment] = useState(getIsProdMode() ? 'Prod' : 'Nonprod');
 // this is different then environment
 // this is to hide the dropdown menu in prod (behind nginx)
 const isProduction = process.env.NODE_ENV === 'production';

 const handleEnvironmentChange = (event) => {
  const selectedEnv = event.target.value;

  setEnvironment(selectedEnv);
  if (selectedEnv === "prod") {
   setIsProdMode(true);
  } else {
   setIsProdMode(false);
  }
  setURLForAPICalls()
  window.location.reload(); // Reload to apply the new environment
 };

 const handleNewChatClick = () => {
  console.log('New');
 };

 const handleMenuButtonClick = () => {
  setDropdownVisible(!isDropdownVisible);
 };

 const handleOptionsClick = () => {
  setPopupVisible(true);
  setDropdownVisible(false);
 };

 const handleClosePopup = () => {
  setPopupVisible(false);
 };

 useEffect(() => {
  const handleClickOutside = (event) => {
   if (isPopupVisible && !event.target.closest('.popup')) {
    setPopupVisible(false);
   }
  };

  document.addEventListener('mousedown', handleClickOutside);
  return () => {
   document.removeEventListener('mousedown', handleClickOutside);
  };
 }, [isPopupVisible]);

 return (
  <div className="top-menu">
   <button className="menu-button" onClick={handleMenuButtonClick}>
    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M120-240v-80h720v80H120Zm0-200v-80h720v80H120Zm0-200v-80h720v80H120Z" /></svg>
   </button>

   {isDropdownVisible && (
    <div className="dropdown-menu">
     <div className="dropdown-item" onClick={handleOptionsClick}>Options</div>
    </div>
   )}

   <div className="menu-right">
    {!isProduction && (
     <div className="environment-selector">
      <select id="environment" value={environment} onChange={handleEnvironmentChange}>
       <option value="prod">Prod</option>
       <option value="nonprod">Nonprod</option>
      </select>
     </div>
    )}
    <div className="model-selector">
     <select id="model" value={getTextModelName()} onChange={handleEnvironmentChange}>
      <option value="gpt-4o">GPT-4o</option>
      <option value="gpt-3.5">GPT-3.5</option>
      <option value="llama">LLama 3 70b</option>
     </select>
    </div>
    <button className="new-chat-button" onClick={handleNewChatClick}>
     <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h280v80H200v560h560v-280h80v280q0 33-23.5 56.5T760-120H200Zm188-212-56-56 372-372H560v-80h280v280h-80v-144L388-332Z" /></svg>
    </button>
   </div>

   {isPopupVisible && (
    <>
     <div className="overlay" onClick={handleClosePopup}></div>
     <div className="popup">
      <OptionsWindow />
     </div>
    </>
   )}
  </div>
 );
};

export default TopMenu;
