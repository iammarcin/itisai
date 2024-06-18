// Main.js

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TopMenu from './TopMenu';
import BottomToolsMenu from './BottomToolsMenu';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import './css/Main.css';

import { setTextAICharacter } from '../utils/local.storage';

const Main = () => {
  // to get sessionId from URL and load the session
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [selectedSession, setSelectedSession] = useState(null);
  const [showCharacterSelection, setShowCharacterSelection] = useState(true);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSelectSession = (session) => {
    navigate(`/session/${session.session_id}`);
    setSelectedSession(session);
    setShowCharacterSelection(false);
  };

  const handleOnNewChatClicked = () => {
    navigate(`/`);
    setShowCharacterSelection(true);
    setSelectedSession(null);
    setUserInput('');
    setIsLoading(false);
    setTextAICharacter('assistant');
  }

  return (
    <div className="layout">
      <TopMenu
        onNewChatClicked={handleOnNewChatClicked}
      />
      <div className="main-content">
        <Sidebar
          onSelectSession={handleSelectSession}
        />
        <div className="chat-area">
          <ChatWindow
            sessionId={sessionId}
            selectedSession={selectedSession}
            showCharacterSelection={showCharacterSelection}
            setShowCharacterSelection={setShowCharacterSelection}
          />
          <BottomToolsMenu
            userInput={userInput}
            setUserInput={setUserInput}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
};

export default Main;
