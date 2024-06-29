// TopMenu.js

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import OptionsWindow from './OptionsWindow';
import './css/TopMenu.css';

import { getIsProdMode, setIsProdMode, setURLForAPICalls, getTextModelName, setTextModelName, setTextAICharacter } from '../utils/configuration';

const TopMenu = ({ onNewChatClicked, currentSessionIndex, setCurrentSessionIndex, setCurrentSessionId, setShouldSkipSessionFetching, chatContent, setChatContent, setShowCharacterSelection, setErrorMsg }) => {
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

  // top left menu
  const handleMenuButtonClick = () => {
    setDropdownVisible(!isDropdownVisible);
  };

  // options button within top left menu
  const handleOptionsClick = () => {
    setPopupVisible(true);
    setDropdownVisible(false);
  };

  const handleClosePopup = () => {
    setPopupVisible(false);
  };

  // on top we have those circle buttons to switch between chat sessions
  // this is choosing specific session / button
  const handleSessionClick = (sessionIndex) => {
    setCurrentSessionIndex(sessionIndex);
    const newSessionId = chatContent[sessionIndex].sessionId;
    if (newSessionId) {
      // set the flag NOT to fetch sessions (handled in Main.js)
      setShouldSkipSessionFetching(true);
      setCurrentSessionId(newSessionId);
      navigate(`/session/${newSessionId}`);
      setShowCharacterSelection(false);
      // if there is character set for this session (must be!) - lets set it globally
      if (chatContent[sessionIndex].ai_character_name) {
        setTextAICharacter(chatContent[sessionIndex].ai_character_name);
      }
    } else {
      setCurrentSessionId(null);
      navigate(`/`);
      setShowCharacterSelection(true);
    }

  };

  // closing session - circle button 
  const handleSessionClose = (sessionIndex) => {
    setChatContent((prevChatContent) => {
      const newSessions = prevChatContent.filter((_, index) => index !== sessionIndex);

      // Ensure the current session index is updated correctly
      const newIndex = sessionIndex > 0 ? sessionIndex - 1 : 0;
      setCurrentSessionIndex(newIndex);
      // get sessionId of newIndex (if it's set) - to make sure that if we switch back - data will be properly loaded (in fact fetchChatContent will be executed)
      const newSessionId = newSessions[newIndex].sessionId;
      if (newSessionId) {
        setCurrentSessionId(newSessionId);
        setShowCharacterSelection(false);
      } else {
        setShowCharacterSelection(true);
      }
      return newSessions;
    });
  };

  // add new session - via top circle buttons
  const handleSessionAdd = () => {
    navigate(`/`);
    setCurrentSessionId(null);
    const newSessionId = chatContent.length;
    const newSession = {
      id: newSessionId,
      messages: []
    };
    setCurrentSessionIndex(newSessionId);

    setChatContent((prevChatContent) => {
      const updatedChatContent = [...prevChatContent, newSession];
      return updatedChatContent;
    });
    setErrorMsg('');
    setTextAICharacter('assistant');
    setShowCharacterSelection(true);
  }

  // if clicked outside of popup window - we want to hide it
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
