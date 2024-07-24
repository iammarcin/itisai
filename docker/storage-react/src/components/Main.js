// Main.js

import React, { useEffect, useCallback, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import { StateContext } from './StateContextProvider';
import useChatAPI from '../hooks/useChatAPI';

import TopMenu from './TopMenu';
import BottomToolsMenu from './BottomToolsMenu';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import ProgressIndicator from './ProgressIndicator';
import './css/Main.css';

import config from '../config';

import { setTextAICharacter, getTextModelName } from '../utils/configuration';

const Main = () => {
  // to get sessionId from URL and load the session
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const {
    setChatContent, currentSessionIndex,
    setCurrentSessionId, setFetchSessionId,
    shouldSkipSessionFetching, setShouldSkipSessionFetching,
    setShowCharacterSelection, readyForRegenerate, setReadyForRegenerate,
    progressBarMessage, userInput, setUserInput,
    editingMessage, attachedImages, setAttachedImages,
    attachedFiles, setAttachedFiles,
    currentSessionIndexRef,
    setIsLoading, errorMsg, setErrorMsg,
  } = useContext(StateContext);

  // custom hook
  const { callChatAPI } = useChatAPI();

  // if URL consists of sessionId
  useEffect(() => {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("sessionId set to: ", sessionId)
    }
    setCurrentSessionId(sessionId);
    if (!shouldSkipSessionFetching) {
      setFetchSessionId(sessionId);
    }
  }, [sessionId, shouldSkipSessionFetching, setCurrentSessionId, setFetchSessionId]);

  // Update ref every time currentSessionIndex changes (use cases above)
  useEffect(() => {
    currentSessionIndexRef.current = currentSessionIndex;
  }, [currentSessionIndex, currentSessionIndexRef]);

  // this is executable in case session is chosen in Sidebar
  const handleSelectSession = (session) => {
    if (config.DEBUG === 1) {
      console.log("session selected: ", session)
    }
    setShouldSkipSessionFetching(false);
    setCurrentSessionId(session.session_id);
    navigate(`/session/${session.session_id}`);
    setShowCharacterSelection(false);
    setTextAICharacter(session.ai_character_name);
  };

  // new chat session (in top menu) clicked - pretty much reset
  const handleOnNewChatClicked = () => {
    setFetchSessionId(null);
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
    setAttachedFiles([]);
    setIsLoading(false);
    setErrorMsg('');
    setTextAICharacter('assistant');
  }

  const handleSendClick = useCallback(() => {
    setErrorMsg('');
    const modelName = getTextModelName();
    if (userInput.trim() === '') {
      setErrorMsg("Please provide your input");
      return;
    }
    if (attachedImages.length > 0 && modelName !== 'GPT-4o' && modelName !== 'GPT-4o-mini' && modelName !== 'GPT-4' && modelName !== 'Claude-3.5') {
      setErrorMsg("Currently chosen model does not support images. Remove image or change the model");
      return;
    }
    if (attachedFiles.length > 0 && modelName !== 'GPT-4o' && modelName !== 'GPT-4' && modelName !== 'Claude-3.5') {
      setErrorMsg("In order to process attached files you need to change the model");
      return;
    }
    if (editingMessage !== null) {
      callChatAPI(editingMessage);
    } else {
      callChatAPI();
    }
    setUserInput("");
    setAttachedImages([]);
    setAttachedFiles([]);
  }, [attachedImages, attachedFiles, userInput, editingMessage, callChatAPI, setAttachedFiles, setAttachedImages, setErrorMsg, setUserInput]);


  // we monitor if handleRegenerate in ChatMessage was used
  useEffect(() => {
    if (readyForRegenerate) {
      handleSendClick();
      setReadyForRegenerate(false);
    }
  }, [readyForRegenerate, handleSendClick, setReadyForRegenerate]);

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
          <ChatWindow />
          {progressBarMessage && <ProgressIndicator message={progressBarMessage} />}
          {errorMsg && <div className="bot-error-msg">{errorMsg}</div>}
          <BottomToolsMenu
            handleSendClick={handleSendClick}
          />
        </div>
      </div>
    </div>
  );
};

export default Main;
