// ChatWindow.js

import React, { useEffect, useState, useRef, useCallback } from 'react';
import ChatMessage from './ChatMessage';
import ChatCharacters from './ChatCharacters';
import apiMethods from '../services/api.methods';
import config from '../config';
import './css/ChatWindow.css';

import { setTextAICharacter } from '../utils/configuration';
import { scrollToBottom } from '../utils/misc';

const ChatWindow = ({ sessionId, chatContent, setChatContent, currentSessionIndex, currentSessionId, showCharacterSelection, setShowCharacterSelection, setErrorMsg }) => {
  // if i right click on any message (to show context window) - we need to reset previous context window 
  // if i clicked 2 time on 2 diff messages - two diff context menu were shown
  const [contextMenuIndex, setContextMenuIndex] = useState(null);
  // this is used for scrollToBottom
  const endOfMessagesRef = useRef(null);

  // fetch chat content (for specific session)
  // useCallback in use to ensure that execution is done only once
  const fetchChatContent = useCallback(async (sessionIdToGet) => {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("EXecuting fetchChatContent with sessionIdToGet: ", sessionIdToGet);
    }
    try {
      const userInput = { "session_id": sessionIdToGet };
      const response = await apiMethods.triggerAPIRequest("api/db", "provider.db", "db_get_user_session", userInput);

      const chatHistory = JSON.parse(response.message.result.chat_history);
      setChatContent((prevChatContent) => {
        const updatedChatContent = [...prevChatContent];
        updatedChatContent[currentSessionIndex].sessionId = sessionIdToGet;
        updatedChatContent[currentSessionIndex].messages = Array.isArray(chatHistory) ? chatHistory : [];
        return updatedChatContent;
      });

      setShowCharacterSelection(false);
    } catch (error) {
      setErrorMsg("Problem with fetching data. Try again.");
      console.error('Failed to fetch chat content', error);
    }
  }, [currentSessionIndex, setChatContent, setShowCharacterSelection, setErrorMsg]);


  // if new session created or if session is chosen or initially if session is set in URL - we will fetch session data
  useEffect(() => {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("useEffect sessionId. Values of: currentSessionId, currentSessionIndex: ", currentSessionId, currentSessionIndex);
    }
    if (currentSessionId) {
      fetchChatContent(currentSessionId);
    } else {
      setChatContent((prevChatContent) => {
        const updatedChatContent = [...prevChatContent];
        updatedChatContent[currentSessionIndex].messages = [];
        return updatedChatContent;
      });
    }
  }, [currentSessionId, currentSessionIndex, fetchChatContent, setChatContent]);

  // scroll to bottom
  useEffect(() => {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("chatContent: ", chatContent);
    }
    if (endOfMessagesRef.current) {
      scrollToBottom(endOfMessagesRef.current);
    }
  }, [chatContent]);

  const handleCharacterSelect = (character) => {
    setShowCharacterSelection(false);
    setTextAICharacter(character.nameForAPI);
  };

  // to check if its last message
  // for AI response is simple - because its just last message in chat content
  // but for user request - we need to check little bit more
  const isLastMessage = (index, message) => {
    if (!message) return false;

    if (message.isUserMessage) {
      // Check if the next message exists and is an AI response
      return (index === chatContent.length - 1) ||
        (index === chatContent.length - 2 && !chatContent[index + 1].isUserMessage);
    } else {
      // For AI messages, the original logic works
      return index === chatContent.length - 1;
    }
  };

  return (
    <div className="chat-window">
      {showCharacterSelection ? (
        <ChatCharacters onSelect={handleCharacterSelect} />
      ) : null}
      <div className="messages">
        {chatContent[currentSessionIndex] && chatContent[currentSessionIndex].messages ? (
          chatContent[currentSessionIndex].messages.map((message, index) => (
            <ChatMessage
              key={index}
              index={index}
              message={message}
              isLastMessage={isLastMessage(index, message)}
              isUserMessage={message.isUserMessage}
              contextMenuIndex={contextMenuIndex}
              setContextMenuIndex={setContextMenuIndex}
            />
          ))
        ) : null}
        <div ref={endOfMessagesRef} />
      </div>
    </div>
  );
};

export default ChatWindow;
