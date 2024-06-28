// Main.js

import React, { useEffect, useState } from 'react';
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

const Main = () => {
  // to get sessionId from URL and load the session
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [showCharacterSelection, setShowCharacterSelection] = useState(true);
  // chat content from chat window
  const [chatContent, setChatContent] = useState([
    {
      id: 0,
      messages: [] // Each session starts with an empty array of messages
    }
  ]);
  // this is index of sessions on top menu (in circle buttons) - to identify which button is currently active etc
  const [currentSessionIndex, setCurrentSessionIndex] = useState(0);
  // this is to track current session Id - from DB
  const [currentSessionId, setCurrentSessionId] = useState(null);
  // this is to trigger fetch session in ChatWindow - i was trying to do it with currentSessionId - but was causing re-triggers when changing top menu sessions which i didn't want
  const [fetchSessionId, setFetchSessionId] = useState(null);

  // user input (text + images) from bottom menu
  const [userInput, setUserInput] = useState('');
  const [attachedImages, setAttachedImages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [progressBarMessage, setProgressBarMessage] = useState('');


  // if URL consists of sessionId
  useEffect(() => {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("sessionId set to: ", sessionId)
    }
    setCurrentSessionId(sessionId);
    setFetchSessionId(sessionId);
  }, [sessionId]);

  // this is executable in case session is chosen in Sidebar
  const handleSelectSession = (session) => {
    if (config.DEBUG === 1) {
      console.log("session: ", session)
    }
    navigate(`/session/${session.session_id}`);
    setCurrentSessionId(session.session_id);
    setFetchSessionId(session.session_id);
    setShowCharacterSelection(false);
    setTextAICharacter(session.ai_character_name);
    const chatHistory = session.chat_history;
    setChatContent((prevChatContent) => {
      const updatedChatContent = [...prevChatContent];
      updatedChatContent[currentSessionIndex].sessionId = session.session_id;
      updatedChatContent[currentSessionIndex].messages = Array.isArray(chatHistory) ? chatHistory : [];
      return updatedChatContent;
    });
  };

  // new chat session (in top menu) clicked - pretty much reset
  const handleOnNewChatClicked = () => {
    navigate(`/`);
    setChatContent([
      {
        id: 0,
        messages: []
      }
    ]);
    setShowCharacterSelection(true);
    setCurrentSessionId(null);
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

  // generate text API call (and potentially image)
  const callChatAPI = async () => {
    setShowCharacterSelection(false);
    setErrorMsg('');

    try {
      //those 2 to be sure that we're generating data for proper session (if user switches or whatever happens)
      // session Id from DB
      const sessionIdForAPI = currentSessionId;
      // session index (top menu circle button)
      const sessionIndexForAPI = currentSessionIndex;

      await ChatHandleAPI({
        userInput, attachedImages,
        sessionIndexForAPI, sessionIdForAPI, currentSessionId, setCurrentSessionId,
        chatContent, setChatContent,
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
        setCurrentSessionId={setCurrentSessionId}
        chatContent={chatContent}
        setChatContent={setChatContent}
        setShowCharacterSelection={setShowCharacterSelection}
        setErrorMsg={setErrorMsg}
        setTextAICharacter={setTextAICharacter}
      />
      <div className="main-content">
        <Sidebar
          onSelectSession={handleSelectSession}
          currentSessionId={currentSessionId}
          setCurrentSessionId={setCurrentSessionId}
          setErrorMsg={setErrorMsg}
        />
        <div className="chat-area">
          <ChatWindow
            sessionId={sessionId}
            chatContent={chatContent}
            setChatContent={setChatContent}
            currentSessionIndex={currentSessionIndex}
            currentSessionId={currentSessionId}
            fetchSessionId={fetchSessionId}
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
