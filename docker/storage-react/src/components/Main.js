// Main.js

import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TopMenu from './TopMenu';
import BottomToolsMenu from './BottomToolsMenu';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import ProgressIndicator from './ProgressIndicator';
import ChatHandleAPI from './ChatHandleAPI';
import './css/Main.css';

import config from '../config';

import { setTextAICharacter, getTextModelName } from '../utils/configuration';

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
  // this is to trigger fetch session in ChatWindow - this together with shouldSkipSessionFetching - will determine if we should fetchChatContent or not
  const [fetchSessionId, setFetchSessionId] = useState(null);
  // used in tandem with above - it will be set to false in most cases (by default so when user just provides URL, or when we click on Sidebar and we want session to be fetched) 
  // but sometimes will be set to true (for example in TopMenu when clicking between sessions) - because then we just want to navigate to URL but don't want sessions to be fetched (because they are already there)
  const [shouldSkipSessionFetching, setShouldSkipSessionFetching] = useState(false);
  // this is to avoid fetchChatContent on changing of currentSessionIndex (when switching top menu sessions) - IMPORTANT! 
  // and also for scrollToBottom function (to be sure that we're scrolling if we are generating data from APIs in active session only)
  const currentSessionIndexRef = useRef(currentSessionIndex);
  // used for editing messages
  const [editingMessage, setEditingMessage] = useState(null);

  // user input (text + images) from bottom menu
  const [userInput, setUserInput] = useState('');
  const [attachedImages, setAttachedImages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [progressBarMessage, setProgressBarMessage] = useState('');
  // this will be used to focus (make active) userInput text area from BottomToolsMenu - so i don't need to click on it to start typing
  const [focusInput, setFocusInput] = useState(false);
  // this will be used to force refresh of chat sessions in Sidebar (when new session is created)
  const [refreshChatSessions, setRefreshChatSessions] = useState(false);
  // (from ChatWindow) this is used for scrollToBottom
  const endOfMessagesRef = useRef(null);

  // if URL consists of sessionId
  useEffect(() => {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("sessionId set to: ", sessionId)
    }
    setCurrentSessionId(sessionId);
    if (!shouldSkipSessionFetching) {
      setFetchSessionId(sessionId);
    }
  }, [sessionId, shouldSkipSessionFetching]);

  // Update ref every time currentSessionIndex changes (use cases above)
  useEffect(() => {
    currentSessionIndexRef.current = currentSessionIndex;
  }, [currentSessionIndex]);

  // this is executable in case session is chosen in Sidebar
  const handleSelectSession = (session) => {
    if (config.DEBUG === 1) {
      console.log("session selected: ", session)
    }
    setShouldSkipSessionFetching(false);
    navigate(`/session/${session.session_id}`);
    setCurrentSessionId(session.session_id);
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

  const handleSendClick = () => {
    setErrorMsg('');
    const modelName = getTextModelName();
    if (attachedImages.length > 0 && modelName !== 'GPT-4o' && modelName !== 'GPT-4') {
      setErrorMsg("Currently chosen model does not support images. Remove image or change the model");
      return;
    }
    if (editingMessage !== null) {
      callChatAPI(editingMessage);
    } else {
      callChatAPI();
    }
    setUserInput("");
    setAttachedImages([]);
  };

  // generate text API call (and potentially image)
  // if editMessagePosition is not null - it means it is edited message
  const callChatAPI = async (editMessagePosition = null) => {
    setShowCharacterSelection(false);
    setErrorMsg('');

    try {
      //those 2 to be sure that we're generating data for proper session (if user switches or whatever happens)
      // session Id from DB
      const sessionIdForAPI = currentSessionId;
      // session index (top menu circle button)
      const sessionIndexForAPI = currentSessionIndex;

      await ChatHandleAPI({
        userInput, editMessagePosition, attachedImages,
        sessionIndexForAPI, sessionIdForAPI, setCurrentSessionId,
        chatContent, setChatContent, setFocusInput, setRefreshChatSessions,
        setIsLoading, setErrorMsg, manageProgressText, scrollToBottom
      });

      // reset edit message position
      if (editMessagePosition !== null) {
        setEditingMessage(null);
      }
    } catch (e) {
      setIsLoading(false);
    }
  };

  const scrollToBottom = (whichChat) => {
    if (whichChat === currentSessionIndexRef.current) {
      endOfMessagesRef.current.scrollIntoView({
        behavior: 'smooth',
      });
    }
  };

  return (
    <div className="layout">
      <TopMenu
        onNewChatClicked={handleOnNewChatClicked}
        currentSessionIndex={currentSessionIndex}
        setCurrentSessionIndex={setCurrentSessionIndex}
        setCurrentSessionId={setCurrentSessionId}
        setShouldSkipSessionFetching={setShouldSkipSessionFetching}
        chatContent={chatContent}
        setChatContent={setChatContent}
        setShowCharacterSelection={setShowCharacterSelection}
        setErrorMsg={setErrorMsg}
      />
      <div className="main-content">
        <Sidebar
          onSelectSession={handleSelectSession}
          currentSessionId={currentSessionId}
          setCurrentSessionId={setCurrentSessionId}
          refreshChatSessions={refreshChatSessions}
          setErrorMsg={setErrorMsg}
        />
        <div className="chat-area">
          <ChatWindow
            chatContent={chatContent}
            setChatContent={setChatContent}
            currentSessionIndex={currentSessionIndex}
            currentSessionIndexRef={currentSessionIndexRef}
            currentSessionId={currentSessionId}
            fetchSessionId={fetchSessionId}
            endOfMessagesRef={endOfMessagesRef}
            showCharacterSelection={showCharacterSelection}
            setShowCharacterSelection={setShowCharacterSelection}
            setEditingMessage={setEditingMessage}
            setUserInput={setUserInput}
            setFocusInput={setFocusInput}
            setErrorMsg={setErrorMsg}
            manageProgressText={manageProgressText}
          />
          {progressBarMessage && <ProgressIndicator message={progressBarMessage} />}
          {errorMsg && <div className="bot-error-msg">{errorMsg}</div>}
          <BottomToolsMenu
            userInput={userInput}
            setUserInput={setUserInput}
            attachedImages={attachedImages}
            setAttachedImages={setAttachedImages}
            setShowCharacterSelection={setShowCharacterSelection}
            handleSendClick={handleSendClick}
            focusInput={focusInput}
            setFocusInput={setFocusInput}
            isLoading={isLoading}
            setErrorMsg={setErrorMsg}
          />
        </div>
      </div>
    </div>
  );
};

export default Main;
