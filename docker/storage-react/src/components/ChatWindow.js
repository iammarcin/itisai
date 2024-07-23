// ChatWindow.js

import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatMessage from './ChatMessage';
import ChatCharacters from './ChatCharacters';
import apiMethods from '../services/api.methods';
import config from '../config';
import './css/ChatWindow.css';

import { setTextAICharacter } from '../utils/configuration';

const ChatWindow = ({ chatContent, setChatContent, setAttachedImages, setAttachedFiles, currentSessionIndex, currentSessionIndexRef, currentSessionId, setCurrentSessionId, fetchSessionId, endOfMessagesRef, showCharacterSelection, setShowCharacterSelection, setEditingMessage, setUserInput, setFocusInput, setErrorMsg, setReadyForRegenerate, manageProgressText, mScrollToBottom }) => {
  const navigate = useNavigate();
  // if i right click on any message (to show context window) - we need to reset previous context window 
  // if i clicked 2 time on 2 diff messages - two diff context menu were shown
  const [contextMenuIndex, setContextMenuIndex] = useState(null);
  // chat content loaded - so we can scroll to bottom (and we need to separate it to make sure that scroll is executed AFTER chat content is loaded)
  const [contentLoaded, setContentLoaded] = useState(false);

  // fetch chat content (for specific session)
  // useCallback in use to ensure that execution is done only once
  const fetchChatContent = useCallback(async (sessionIdToGet) => {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("EXecuting fetchChatContent with sessionIdToGet: ", sessionIdToGet);
    }
    // this hopefully won't be in use - but just in case added here
    // due to async nature of react - this was executed twice (for session that we were switching from too)
    // so this is to avoid it
    if (sessionIdToGet !== currentSessionId) {
      if (config.VERBOSE_SUPERB === 1) {
        console.log("Skipping fetch for outdated session:", sessionIdToGet);
      }
      return;
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

        setTextAICharacter(response.message.result.ai_character_name);

        setShowCharacterSelection(false);
        // content loaded - so we can trigger scroll to bottom
        setContentLoaded(true);
      }
    } catch (error) {
      setErrorMsg("Problem with fetching data. Try again.");
      console.error('Failed to fetch chat content', error);
    }
  }, [currentSessionId, currentSessionIndexRef, setChatContent, navigate, setCurrentSessionId, setShowCharacterSelection, setErrorMsg]);


  // if new session created or if session is chosen or initially if session is set in URL - we will fetch session data
  useEffect(() => {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("useEffect fetchSessionId. Values of: fetchSessionId, currentSessionId, currentSessionIndex: ", fetchSessionId, currentSessionId, currentSessionIndexRef.current);
    }

    // if there is sessionId - we fetch specific session data from DB
    // (added later) - but only if we are supposed to fetch current chosen session Id
    // due to async of useEffect - it was executed twice
    if (fetchSessionId && fetchSessionId === currentSessionId) {
      fetchChatContent(fetchSessionId);
    } else if (fetchSessionId === null) {
      // if fetchSessionId is not provided - we just set empty array for future messages
      setChatContent((prevChatContent) => {
        const updatedChatContent = [...prevChatContent];
        updatedChatContent[currentSessionIndexRef.current].messages = [];
        return updatedChatContent;
      });
    }
  }, [fetchSessionId, currentSessionId, currentSessionIndexRef, fetchChatContent, setChatContent]);

  // once chat content loaded - we can scroll to bottom finally
  useEffect(() => {
    if (contentLoaded) {
      mScrollToBottom(currentSessionIndexRef.current, false);
      setContentLoaded(false); // Reset for future loads
    }
  }, [contentLoaded, currentSessionIndexRef, mScrollToBottom]);

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
              setAttachedFiles={setAttachedFiles}
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
