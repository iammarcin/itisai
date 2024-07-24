// FloatingChat.js

import React, { useState, useRef } from 'react';
import { ResizableBox } from 'react-resizable';
import 'react-resizable/css/styles.css';
import './css/FloatingChat.css';

import BottomToolsMenu from '../BottomToolsMenu';
import ChatMessage from '../ChatMessage';
import apiMethods from '../../services/api.methods';
import { setTextAICharacter } from '../../utils/configuration';
import { characters } from '../ChatCharacters';

const FloatingChat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const [previousSize, setPreviousSize] = useState({ width: 300, height: 400 });

  const [attachedImages, setAttachedImages] = useState([]);
  const [attachedFiles, setAttachedFiles] = useState([]);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [editingMessage, setEditingMessage] = useState(null);
  const [focusInput, setFocusInput] = useState(false);
  const [readyForRegenerate, setReadyForRegenerate] = useState(false);

  const inputRef = useRef(null);
  const endOfMessagesRef = useRef(null);

  const [contextMenuIndex, setContextMenuIndex] = useState(null);

  // Assuming you're using a single session in the floating chat
  const currentSessionIndex = 0;
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [chatContent, setChatContent] = useState([{ messages: [] }]);

  const handleSendClick = async () => {
    if (input.trim() || attachedImages.length > 0 || attachedFiles.length > 0) {
      setIsLoading(true);
      const newUserMessage = {
        isUserMessage: true,
        message: input,
        imageLocations: attachedImages.map(img => img.preview),
        fileNames: attachedFiles.map(file => file.name),
      };

      let updatedMessages;
      if (editingMessage) {
        updatedMessages = [...messages];
        updatedMessages[editingMessage.index] = newUserMessage;
        // Remove the next AI message if it exists
        if (editingMessage.index + 1 < updatedMessages.length && !updatedMessages[editingMessage.index + 1].isUserMessage) {
          updatedMessages.splice(editingMessage.index + 1, 1);
        }
      } else {
        updatedMessages = [...messages, newUserMessage];
      }

      setMessages(updatedMessages);
      setInput('');
      setAttachedImages([]);
      setAttachedFiles([]);
      setEditingMessage(null);

      try {

        // Assuming you're using a default AI character for the floating chat
        const defaultCharacter = characters[0];
        /*
        setTextAICharacter(defaultCharacter.nameForAPI);

        const response = await apiMethods.sendMessageToAPI(input, attachedImages, attachedFiles, defaultCharacter.nameForAPI);

        const newAIMessage = {
          isUserMessage: false,
          message: response.message,
          imageLocations: response.imageLocations || [],
          fileNames: response.fileNames || [],
          aiCharacterName: defaultCharacter.nameForAPI,
          apiAIModelName: response.apiAIModelName,
          dateGenerate: new Date().toLocaleString(),
        };

        setMessages([...updatedMessages, newAIMessage]);

        // Update chatContent for consistency with the main chat
        setChatContent([{ messages: [...updatedMessages, newAIMessage] }]);
        */
      } catch (error) {
        setErrorMsg("Error in sending message. Please try again.");
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const handleResizeStop = (event, { size }) => {
    setPreviousSize(size);
  };

  const manageProgressText = (action, type) => {
    // Implement if needed
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
                <ChatMessage
                  key={index}
                  index={index}
                  message={msg}
                  isLastMessage={index === messages.length - 1}
                  isUserMessage={msg.isUserMessage}
                  contextMenuIndex={contextMenuIndex}
                  setContextMenuIndex={setContextMenuIndex}
                  currentSessionIndex={currentSessionIndex}
                  currentSessionId={currentSessionId}
                  setCurrentSessionId={setCurrentSessionId}
                  chatContent={chatContent}
                  setChatContent={setChatContent}
                  setAttachedImages={setAttachedImages}
                  setAttachedFiles={setAttachedFiles}
                  setEditingMessage={setEditingMessage}
                  setUserInput={setInput}
                  setFocusInput={setFocusInput}
                  manageProgressText={manageProgressText}
                  setReadyForRegenerate={setReadyForRegenerate}
                  setErrorMsg={setErrorMsg}
                />
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
