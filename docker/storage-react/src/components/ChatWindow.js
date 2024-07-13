// ChatWindow.js

import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatMessage from './ChatMessage';
import ChatCharacters from './ChatCharacters';
import apiMethods from '../services/api.methods';
import config from '../config';
import './css/ChatWindow.css';

import { setTextAICharacter } from '../utils/configuration';

const ChatWindow = ({ chatContent, setChatContent, setAttachedImages, currentSessionIndex, currentSessionIndexRef, currentSessionId, setCurrentSessionId, fetchSessionId, endOfMessagesRef, showCharacterSelection, setShowCharacterSelection, setEditingMessage, setUserInput, setFocusInput, setErrorMsg, setReadyForRegenerate, manageProgressText }) => {
  const navigate = useNavigate();
  // if i right click on any message (to show context window) - we need to reset previous context window 
  // if i clicked 2 time on 2 diff messages - two diff context menu were shown
  const [contextMenuIndex, setContextMenuIndex] = useState(null);

  // fetch chat content (for specific session)
  // useCallback in use to ensure that execution is done only once
  const fetchChatContent = useCallback(async (sessionIdToGet) => {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("EXecuting fetchChatContent with sessionIdToGet: ", sessionIdToGet);
    }
    try {
      const userInput = { "session_id": sessionIdToGet };
      const response = await apiMethods.triggerAPIRequest("api/db", "provider.db", "db_get_user_session", userInput);

      // if session doesn't exist
      if (response.code !== 200) {
        setCurrentSessionId(null);
        navigate(`/`);
        setShowCharacterSelection(true);
      } else {
        const chatHistory = response.message.result.chat_history;
        setChatContent((prevChatContent) => {
          const updatedChatContent = [...prevChatContent];
          updatedChatContent[currentSessionIndexRef.current].ai_character_name = response.message.result.ai_character_name;
          updatedChatContent[currentSessionIndexRef.current].sessionId = sessionIdToGet;
          updatedChatContent[currentSessionIndexRef.current].messages = Array.isArray(chatHistory) ? chatHistory : [];
          return updatedChatContent;
        });

        setShowCharacterSelection(false);
      }
    } catch (error) {
      setErrorMsg("Problem with fetching data. Try again.");
      console.error('Failed to fetch chat content', error);
    }
  }, [currentSessionIndexRef, setChatContent, setShowCharacterSelection, setErrorMsg]);


  // if new session created or if session is chosen or initially if session is set in URL - we will fetch session data
  useEffect(() => {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("useEffect fetchSessionId. Values of: fetchSessionId, currentSessionIndex: ", fetchSessionId, currentSessionIndexRef.current);
    }

    // if there is sessionId - we fetch specific session data from DB
    if (fetchSessionId) {
      fetchChatContent(fetchSessionId);
    } else {
      // if it is not provided - we just set empty array for future messages
      setChatContent((prevChatContent) => {
        const updatedChatContent = [...prevChatContent];
        updatedChatContent[currentSessionIndexRef.current].messages = [];
        return updatedChatContent;
      });
    }
  }, [fetchSessionId, currentSessionIndexRef, fetchChatContent, setChatContent]);

  const handleCharacterSelect = (character) => {
    setShowCharacterSelection(false);
    setTextAICharacter(character.nameForAPI);
  };

  // to check if its last message
  // for AI response is simple - because its just last message in chat content
  // but for user request - we need to check little bit more
  const isLastMessage = (index, message) => {
    if (!message) return false;
    const currentChatContent = chatContent[currentSessionIndex].messages;

    if (message.isUserMessage) {
      // Check if the next message exists and is an AI response
      return (index === currentChatContent.length - 1) ||
        (index === currentChatContent.length - 2 && !currentChatContent[index + 1].isUserMessage);
    } else {
      // For AI messages, the original logic works
      return index === currentChatContent.length - 1;
    }
  };

  // Debugging only in super verbose mode
  useEffect(() => {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("Chat content: ", chatContent);
    }
  }, [chatContent]);

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
              currentSessionIndex={currentSessionIndex}
              currentSessionId={currentSessionId}
              setCurrentSessionId={setCurrentSessionId}
              chatContent={chatContent}
              setChatContent={setChatContent}
              setAttachedImages={setAttachedImages}
              setEditingMessage={setEditingMessage}
              setUserInput={setUserInput}
              setFocusInput={setFocusInput}
              manageProgressText={manageProgressText}
              setReadyForRegenerate={setReadyForRegenerate}
              setErrorMsg={setErrorMsg}
            />
          ))
        ) : null}
        <div ref={endOfMessagesRef} />
      </div>
    </div>
  );
};

export default ChatWindow;
