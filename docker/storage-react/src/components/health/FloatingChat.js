// FloatingChat.js

import React, { useState, useRef } from 'react';
import { ResizableBox } from 'react-resizable';
import 'react-resizable/css/styles.css';
import './css/FloatingChat.css';

import BottomToolsMenu from '../BottomToolsMenu';
import ChatMessage from '../ChatMessage';

const FloatingChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const [previousSize, setPreviousSize] = useState({ width: 300, height: 400 });

  const [attachedImages, setAttachedImages] = useState([]);
  const [attachedFiles, setAttachedFiles] = useState([]);

  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef(null);
  const endOfMessagesRef = useRef(null);

  const handleSendClick = () => {
    if (input.trim()) {
      setMessages([...messages, { isUserMessage: true, message: input }]);
      setInput('');
      // Handle sending message to API and receiving response
    }
  };

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
              {messages.map((msg, index) => (
                <div key={index} className="floating-chat-message">
                  {msg}
                </div>
              ))}
            </div>
            <BottomToolsMenu
              userInput={input}
              setUserInput={setInput}
              attachedImages={attachedImages}
              setAttachedImages={setAttachedImages}
              attachedFiles={attachedFiles}
              setAttachedFiles={setAttachedFiles}
              handleSendClick={handleSendClick}
              focusInput={false}
              setFocusInput={() => { }}
              isLoading={false}
              setErrorMsg={() => { }}
              isFloating={true}
            />
          </div>
        </ResizableBox>
      )}
    </div>
  );
};


export default FloatingChat;
