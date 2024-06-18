// Main.js

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TopMenu from './TopMenu';
import BottomToolsMenu from './BottomToolsMenu';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import ChatHandleAPI from './ChatHandleAPI';
import './css/Main.css';

import { setTextAICharacter } from '../utils/local.storage';

const Main = () => {
  // to get sessionId from URL and load the session
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [selectedSession, setSelectedSession] = useState(null);
  const [showCharacterSelection, setShowCharacterSelection] = useState(true);
  // chat content from chat window
  const [chatContent, setChatContent] = useState(null);
  // user input from bottom menu
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

  const callChatAPI = async (userInput) => {
    try {
      console.log("callChatAPI")
      const resp = await ChatHandleAPI({
        userInput, chatContent, setChatContent, setIsLoading
      });
      console.log("resp", resp)
    } catch (e) {
      setIsLoading(false);
    }
  };

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
            chatContent={chatContent}
            setChatContent={setChatContent}
            showCharacterSelection={showCharacterSelection}
            setShowCharacterSelection={setShowCharacterSelection}
          />
          <BottomToolsMenu
            userInput={userInput}
            setUserInput={setUserInput}
            callChatAPI={callChatAPI}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
};

export default Main;
