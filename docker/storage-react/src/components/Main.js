// Main.js

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TopMenu from './TopMenu';
import BottomToolsMenu from './BottomToolsMenu';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import ProgressIndicator from './ProgressIndicator';
import ChatHandleAPI from './ChatHandleAPI';
import './css/Main.css';

import config from '../config';

import { setTextAICharacter } from '../utils/configuration';
import { setCurrentSessionId } from '../utils/session.utils';

const Main = () => {
  // to get sessionId from URL and load the session
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [selectedSession, setSelectedSession] = useState(null);
  const [showCharacterSelection, setShowCharacterSelection] = useState(true);
  // chat content from chat window
  const [chatContent, setChatContent] = useState([
    {
      id: 0,
      messages: [] // Each session starts with an empty array of messages
    }
  ]);
  const [currentSessionIndex, setCurrentSessionIndex] = useState(0);

  // user input (text + images) from bottom menu
  const [userInput, setUserInput] = useState('');
  const [attachedImages, setAttachedImages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [progressBarMessage, setProgressBarMessage] = useState('');

  const handleSelectSession = (session) => {
    if (config.DEBUG === 1) {
      console.log("session: ", session)
    }
    navigate(`/session/${session.session_id}`);
    setSelectedSession(session);
    setCurrentSessionId(session.session_id);
    setShowCharacterSelection(false);
    setTextAICharacter(session.ai_character_name);
    const chatHistory = JSON.parse(session.chat_history);
    setChatContent((prevChatContent) => {
      const updatedChatContent = [...prevChatContent];
      updatedChatContent[currentSessionIndex].sessionId = session.session_id;
      updatedChatContent[currentSessionIndex].messages = Array.isArray(chatHistory) ? chatHistory : [];
      return updatedChatContent;
    });
  };

  const handleOnNewChatClicked = () => {
    navigate(`/`);
    setChatContent([]);
    setShowCharacterSelection(true);
    setSelectedSession(null);
    setUserInput('');
    setAttachedImages([]);
    setIsLoading(false);
    setErrorMsg('');
    setTextAICharacter('assistant');
  }

  // this is showProgress, hideProgress merged in one place
  // accepting method - "show" and "hide"
  // and then adding or removing specific text
  const manageProgressText = (method, text) => {
    if (method === 'show') {
      setProgressBarMessage((prevMessage) => prevMessage ? `${prevMessage} ${text}` : text);
    } else if (method === 'hide') {
      setProgressBarMessage((prevMessage) => {
        const messages = prevMessage.split(' ');
        const filteredMessages = messages.filter((msg) => msg !== text);
        return filteredMessages.join(' ');
      });
    }
  }

  const callChatAPI = async (userInput) => {
    setShowCharacterSelection(false);
    setErrorMsg('');

    try {
      await ChatHandleAPI({
        userInput, attachedImages,
        chatContent: chatContent[currentSessionIndex].messages, // Pass messages of current session
        setChatContent: (newMessages) => {
          const updatedSessions = [...chatContent];
          updatedSessions[currentSessionIndex].messages = newMessages;
          setChatContent(updatedSessions);
        },
        setIsLoading, setErrorMsg, manageProgressText
      });
    } catch (e) {
      setIsLoading(false);
    }
  };



  return (
    <div className="layout">
      <TopMenu
        onNewChatClicked={handleOnNewChatClicked}
        currentSessionIndex={currentSessionIndex}
        setCurrentSessionIndex={setCurrentSessionIndex}
        setSelectedSession={setSelectedSession}
        chatContent={chatContent}
        setChatContent={setChatContent}
      />
      <div className="main-content">
        <Sidebar
          selectedSession={selectedSession}
          setSelectedSession={setSelectedSession}
          onSelectSession={handleSelectSession}
          setErrorMsg={setErrorMsg}
        />
        <div className="chat-area">
          <ChatWindow
            sessionId={sessionId}
            selectedSession={selectedSession}
            chatContent={chatContent}
            setChatContent={setChatContent}
            currentSessionIndex={currentSessionIndex}
            showCharacterSelection={showCharacterSelection}
            setShowCharacterSelection={setShowCharacterSelection}
            setErrorMsg={setErrorMsg}
          />
          {progressBarMessage && <ProgressIndicator message={progressBarMessage} />}
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
