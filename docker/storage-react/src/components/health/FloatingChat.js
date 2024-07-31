// FloatingChat.js

import React, { useState, useEffect, useContext } from 'react';

import { StateContext } from '../StateContextProvider';
import useChatAPI from '../../hooks/useChatAPI';

import { setTextAICharacter, getTextModelName } from '../../utils/configuration';

import { ResizableBox } from 'react-resizable';
import 'react-resizable/css/styles.css';
import './css/FloatingChat.css';

import BottomToolsMenu from '../BottomToolsMenu';
import ChatMessage from '../ChatMessage';

const FloatingChat = ({ data }) => {
  const {
    userInput, setUserInput, chatContent, setAssetInput,
    attachedImages, setAttachedImages, endOfMessagesRef,
    setAttachedFiles, editingMessage,
    errorMsg, setErrorMsg, isMobile,
  } = useContext(StateContext);

  // need to use useState - because before calling chat api - if we want to add more context with data (from Health) - then we need to wait until data is updated (ahh async react - love you )
  const [triggerAPI, setTriggerAPI] = useState(false);

  // custom hook
  const { callChatAPI } = useChatAPI();

  // if i right click on any message (to show context window) - we need to reset previous context window 
  // if i clicked 2 time on 2 diff messages - two diff context menu were shown
  const [contextMenuIndex, setContextMenuIndex] = useState(null);
  const currentSessionIndex = 0;
  const [isMinimized, setIsMinimized] = useState(true);
  const [previousSize, setPreviousSize] = useState({
    width: isMobile ? 335 : 500, height: isMobile ? 300 : 300
  });

  const handleSendClick = () => {
    setErrorMsg('');
    const modelName = getTextModelName();
    // TODO - change!
    setTextAICharacter('sleep_expert');

    if (userInput.trim() === '') {
      setErrorMsg("Please provide your input");
      return;
    }

    if (attachedImages.length > 0 && modelName !== 'GPT-4o' && modelName !== 'GPT-4o-mini' && modelName !== 'GPT-4' && modelName !== 'Claude-3.5') {
      setErrorMsg("Currently chosen model does not support images. Remove image or change the model");
      return;
    }

    // attach context (data)
    setAssetInput(data)

    // Set the trigger to call API
    setTriggerAPI(true);
  };

  useEffect(() => {
    if (triggerAPI) {
      if (editingMessage !== null) {
        callChatAPI(editingMessage);
      } else {
        callChatAPI();
      }
      setTriggerAPI(false); // Reset the trigger

      setUserInput("");
      setAssetInput([]);
      setAttachedImages([]);
      setAttachedFiles([]);
    }
  }, [userInput, triggerAPI, callChatAPI, editingMessage, setUserInput, setAssetInput, setAttachedImages, setAttachedFiles]);

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const handleResizeStop = (event, { size }) => {
    setPreviousSize(size);
  };

  return (
    <div className="floating-chat-container">
      {isMinimized ? (
        <button onClick={toggleMinimize} className="floating-chat-minimizedButton">
          <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M120-120v-320h80v184l504-504H520v-80h320v320h-80v-184L256-200h184v80H120Z" /></svg>
        </button>
      ) : (
        <ResizableBox
          width={previousSize.width}
          height={previousSize.height}
          minConstraints={[200, 200]}
          maxConstraints={[window.innerWidth, window.innerHeight]}
          className="floating-chat-resizableBox"
          resizeHandles={['se', 'sw', 'ne', 'nw', 'n', 's', 'e', 'w']}
          onResizeStop={handleResizeStop}
        >
          <div className="floating-chat-box">
            <button onClick={toggleMinimize} className="floating-chat-minimizeButton">
              <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="m136-80-56-56 264-264H160v-80h320v320h-80v-184L136-80Zm344-400v-320h80v184l264-264 56 56-264 264h184v80H480Z" /></svg>
            </button>
            <div className="floating-chat-messages">
              {chatContent[currentSessionIndex] && chatContent[currentSessionIndex].messages ? (
                chatContent[currentSessionIndex].messages.map((message, index) => (
                  <ChatMessage
                    key={index}
                    index={index}
                    message={message}
                    isLastMessage={index === chatContent[currentSessionIndex].messages.length - 1}
                    isUserMessage={message.isUserMessage}
                    contextMenuIndex={contextMenuIndex}
                    setContextMenuIndex={setContextMenuIndex}
                    isFloating={true}
                  />
                ))
              ) : null}
              <div ref={endOfMessagesRef} />
            </div>
            {errorMsg && <div className="bot-error-msg">{errorMsg}</div>}
            <BottomToolsMenu
              handleSendClick={handleSendClick}
              isFloating={true}
            />
          </div>
        </ResizableBox>
      )}
    </div>
  );
};


export default FloatingChat;
