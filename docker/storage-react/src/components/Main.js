// Main.js

import React, { useEffect, useRef, useCallback, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import { StateContext } from './StateContextProvider';

import TopMenu from './TopMenu';
import BottomToolsMenu from './BottomToolsMenu';
import Sidebar from './Sidebar';
import ChatWindow from './ChatWindow';
import ProgressIndicator from './ProgressIndicator';
import ChatHandleAPI from './ChatHandleAPI';
import './css/Main.css';

import config from '../config';

import { getTextAICharacter, setTextAICharacter, getTextModelName } from '../utils/configuration';

// function put outside of Main component - because it triggered re-renders from different places
const scrollToBottom = (whichChat, smooth = true, endOfMessagesRef, currentSessionIndexRef) => {
  if (whichChat === currentSessionIndexRef.current) {
    // smooth not needed - for example when restoring session
    var behavior = 'auto';
    if (smooth)
      behavior = 'smooth';
    endOfMessagesRef.current.scrollIntoView({
      behavior: behavior,
    });
  }


  // i tried few different methods - didn't really work well
  /*const chatWindowContainer = document.querySelector('.bottom-tools-menu');
  const isAtBottom = chatWindowContainer.scrollHeight - chatWindowContainer.scrollTop <= chatWindowContainer.clientHeight + 70;
  console.log("isAtBottom: ", isAtBottom);*/
  /*if (isAtBottom) {
    console.log("scrolling to bottom")

    console.log(whichChat)
    console.log(currentSessionIndexRef.current)
    if (whichChat === currentSessionIndexRef.current) {
      console.log("scrolling to bottom2")
      //const scrollTargetPosition = botTextAreaContainer.getBoundingClientRect().top - window.innerHeight + botTextAreaContainer.offsetHeight;

      // Scroll smoothly to the target position
      /*window.scrollBy({
        top: chatWindowContainer.getBoundingClientRect().bottom,
        behavior: 'smooth',
      });*/
  /*endOfMessagesRef.current.scrollIntoView({
    behavior: 'smooth',
  });
}
}*/
};

const Main = () => {
  // to get sessionId from URL and load the session
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const {
    chatContent, setChatContent, currentSessionIndex,
    currentSessionId, setCurrentSessionId, setFetchSessionId,
    shouldSkipSessionFetching, setShouldSkipSessionFetching,
    setShowCharacterSelection, setFocusInput,
    readyForRegenerate, setReadyForRegenerate,
    setRefreshChatSessions, progressBarMessage,
    userInput, setUserInput,
    editingMessage, setEditingMessage,
    attachedImages, setAttachedImages,
    attachedFiles, setAttachedFiles,
    endOfMessagesRef, currentSessionIndexRef,
    setIsLoading, errorMsg, setErrorMsg,
    manageProgressText
  } = useContext(StateContext);

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

  // a memoized version of scroll to bottom (not to trigger re-renders)
  const mScrollToBottom = useCallback((whichChat, smooth = true) => {
    scrollToBottom(whichChat, smooth, endOfMessagesRef, currentSessionIndexRef);
  }, [endOfMessagesRef, currentSessionIndexRef]);

  // generate text API call (and potentially image)
  // if editMessagePosition is not null - it means it is edited message
  const callChatAPI = useCallback(async (editMessagePosition = null) => {
    setShowCharacterSelection(false);
    setErrorMsg('');

    try {
      //those 2 to be sure that we're generating data for proper session (if user switches or whatever happens)
      // session Id from DB
      const sessionIdForAPI = currentSessionId;
      // session index (top menu circle button)
      const sessionIndexForAPI = currentSessionIndex;
      const currentAICharacter = getTextAICharacter();
      const apiAIModelName = getTextModelName();

      await ChatHandleAPI({
        userInput, editMessagePosition, attachedImages, attachedFiles,
        currentSessionIndex, sessionIndexForAPI, sessionIdForAPI, setCurrentSessionId,
        chatContent, setChatContent, currentAICharacter, apiAIModelName, setFocusInput, setRefreshChatSessions,
        setIsLoading, setErrorMsg, manageProgressText, mScrollToBottom
      });

      // reset edit message position
      if (editMessagePosition !== null) {
        setEditingMessage(null);
      }
    } catch (e) {
      setIsLoading(false);
    }
  }, [userInput, attachedImages, attachedFiles, currentSessionId, currentSessionIndex, chatContent, mScrollToBottom]);

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
  }, [attachedImages, attachedFiles, userInput, editingMessage, callChatAPI]);


  // we monitor if handleRegenerate in ChatMessage was used
  useEffect(() => {
    if (readyForRegenerate) {
      handleSendClick();
      setReadyForRegenerate(false);
    }
  }, [readyForRegenerate, handleSendClick]);

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
            mScrollToBottom={mScrollToBottom}
          />
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
