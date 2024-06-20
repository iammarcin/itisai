// Main.js

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TopMenu from './TopMenu';
import BottomToolsMenu from './BottomToolsMenu';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import ChatHandleAPI from './ChatHandleAPI';
import './css/Main.css';

import config from '../config';

import { setTextAICharacter } from '../utils/configuration';

const Main = () => {
  // to get sessionId from URL and load the session
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [sessions, setSessions] = useState({});
  const [currentSessionIndex, setCurrentSessionIndex] = useState(null);
  const [showCharacterSelection, setShowCharacterSelection] = useState(true);
  // user input (text + images) from bottom menu
  const [userInput, setUserInput] = useState('');
  const [attachedImages, setAttachedImages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSelectSession = (session) => {
    if (config.DEBUG === 1) {
      console.log("session: ", session)
    }
    navigate(`/session/${session.session_id}`);
    setCurrentSessionIndex(session.session_id);
    setShowCharacterSelection(false);
    setTextAICharacter(session.ai_character_name);
  };

  const handleOnNewChatClicked = () => {
    navigate(`/`);
    const newSessionId = `session_${Date.now()}`;
    setSessions((prevSessions) => ({
      ...prevSessions,
      [newSessionId]: [],
    }));
    setCurrentSessionIndex(newSessionId);
    setShowCharacterSelection(true);
    setUserInput('');
    setAttachedImages([]);
    setIsLoading(false);
    setErrorMsg('');
    setTextAICharacter('assistant');
  }

  const callChatAPI = async (userInput) => {
    setShowCharacterSelection(false);
    setErrorMsg('');

    try {
      await ChatHandleAPI({
        userInput,
        attachedImages,
        chatContent: sessions[currentSessionIndex],
        setChatContent: (newContent) => {
          setSessions((prevSessions) => ({
            ...prevSessions,
            [currentSessionIndex]: newContent,
          }));
        }, setIsLoading, setErrorMsg
      });
    } catch (e) {
      setIsLoading(false);
    }
  };

  return (
    <div className="layout">
      <TopMenu
        onNewChatClicked={handleOnNewChatClicked}
        sessions={sessions}
        currentSessionIndex={currentSessionIndex}
        setCurrentSessionIndex={setCurrentSessionIndex}
        setSessions={setSessions}
      />
      <div className="main-content">
        <Sidebar
          onSelectSession={handleSelectSession}
          setErrorMsg={setErrorMsg}
        />
        <div className="chat-area">
          <ChatWindow
            sessionId={sessionId}
            currentSessionIndex={currentSessionIndex}
            chatContent={sessions[currentSessionIndex]}
            setChatContent={(newContent) => {
              setSessions((prevSessions) => ({
                ...prevSessions,
                [currentSessionIndex]: newContent,
              }));
            }}
            showCharacterSelection={showCharacterSelection}
            setShowCharacterSelection={setShowCharacterSelection}
            setErrorMsg={setErrorMsg}
          />
          {errorMsg && <div className="bot-error-msg">{errorMsg}</div>}
          <BottomToolsMenu
            userInput={userInput}
            setUserInput={setUserInput}
            attachedImages={attachedImages}
            setAttachedImages={setAttachedImages}
            callChatAPI={callChatAPI}
            isLoading={isLoading}
            setErrorMsg={setErrorMsg}
          />
        </div>
      </div>
    </div>
  );
};

export default Main;
