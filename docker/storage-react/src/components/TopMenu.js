// TopMenu.js

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './css/TopMenu.css';
import { getIsProdMode, setIsProdMode, setURLForAPICalls, getTextModelName, setTextModelName } from '../utils/configuration';
import OptionsWindow from './OptionsWindow';

const TopMenu = ({ onNewChatClicked, currentSessionIndex, setCurrentSessionIndex, setSelectedSession, chatContent, setChatContent }) => {
  const navigate = useNavigate();
  const [isPopupVisible, setPopupVisible] = useState(false);
  const [isDropdownVisible, setDropdownVisible] = useState(false);
  // this is to show value in dropdown menu
  const [textModelName, setLocalTextModelName] = useState(getTextModelName());
  // this is to track if we want to use prod or non prod backend (and will be only available in non prod react)
  const [environment, setEnvironment] = useState(getIsProdMode() ? 'prod' : 'nonprod');
  // this is different then environment
  // this is to hide the dropdown menu in prod (behind nginx)
  const isProduction = process.env.NODE_ENV === 'production';

  const handleTextModelChange = (event) => {
    setTextModelName(event.target.value);
    setLocalTextModelName(event.target.value);
  }

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
    onNewChatClicked()
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

  const handleSessionClick = (sessionIndex) => {
    setCurrentSessionIndex(sessionIndex);
  };

  useEffect(() => {
    console.log("TOP MENU! chatContent: ", chatContent);
  }, [chatContent])

  const handleSessionClose = (sessionIndex) => {
    console.log("Handle session close", sessionIndex);
    console.log("chatContent: ", chatContent);

    setChatContent((prevChatContent) => {
      const newSessions = prevChatContent.filter((_, index) => index !== sessionIndex);
      console.log("newSessions after filter", newSessions);

      // Ensure the current session index is updated correctly
      const newIndex = sessionIndex > 0 ? sessionIndex - 1 : 0;
      // get sessionId of newIndex
      const newSessionId = newSessions[newIndex].sessionId;
      if (newSessionId)
        navigate(`/session/${newSessionId}`);
      setCurrentSessionIndex(newIndex);
      console.log("switching to index : ", newIndex);

      return newSessions;
    });
  };

  const handleSessionAdd = () => {
    navigate(`/`);
    setSelectedSession(null)
    const newSessionId = chatContent.length;
    const newSession = {
      id: newSessionId,
      messages: []
    };
    setCurrentSessionIndex(newSessionId);
    console.log("newSessionId", newSessionId);
    console.log("newSession", newSession);
    setChatContent((prevChatContent) => {
      console.log("Previous chat content:", prevChatContent);
      const updatedChatContent = [...prevChatContent, newSession];
      console.log("Updated chat content:", updatedChatContent);
      return updatedChatContent;
    });


  }

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
      <div className="session-buttons">
        {Object.keys(chatContent).map((sessionId, index) => (
          <div key={sessionId} className={`session-button-container ${currentSessionIndex === index ? 'active' : ''}`}>
            <button
              className={`session-button ${currentSessionIndex === index ? 'active' : ''}`}
              onClick={() => handleSessionClick(index)}
            >
              {index + 1}
            </button>
            <button className="close-button" onClick={() => handleSessionClose(index)}>×</button>
          </div>
        ))}
        {Object.keys(chatContent).length < 5 && (
          <button className="session-button add-session" onClick={handleSessionAdd}>+</button>
        )}
      </div>
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
          <select id="model" value={textModelName} onChange={handleTextModelChange}>
            <option value="GPT-4o">GPT-4o</option>
            <option value="GPT-3.5">GPT-3.5</option>
            <option value="LLama 3 70b">LLama 3 70b</option>
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
