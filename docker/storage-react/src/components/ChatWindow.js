// ChatWindow.js
import React, { useEffect, useState, useRef } from 'react';
import ChatMessage from './ChatMessage';
import ChatCharacters from './ChatCharacters';
import apiMethods from '../services/api.methods';
import config from '../config';
import './css/ChatWindow.css';

import { setTextAICharacter } from '../utils/configuration';
import { scrollToBottom } from '../utils/misc';

const ChatWindow = ({ sessionId, selectedSession, chatContent, setChatContent, currentSessionIndex, showCharacterSelection, setShowCharacterSelection, setErrorMsg }) => {
  // if i right click on any message (to show context window) - we need to reset previous context window 
  // if i clicked 2 time on 2 diff messages - two diff context menu were shown
  const [contextMenuIndex, setContextMenuIndex] = useState(null);
  // this is used for scrollToBottom
  const endOfMessagesRef = useRef(null);

  // fetch chat content (for specific session)
  useEffect(() => {
    const fetchChatContent = async (sessionIdToGet) => {
      try {
        const userInput = { "session_id": sessionIdToGet };
        const response = await apiMethods.triggerAPIRequest("api/db", "provider.db", "db_get_user_session", userInput);

        const chatHistory = JSON.parse(response.message.result.chat_history);
        chatContent[currentSessionIndex].messages = Array.isArray(chatHistory) ? chatHistory : [];

        //setChatContent(Array.isArray(chatHistory) ? chatHistory : []);
        setShowCharacterSelection(false);
      } catch (error) {
        setErrorMsg("Problem with fetching data. Try again.");
        console.error('Failed to fetch chat content', error);
      }
    };

    if (sessionId) {
      fetchChatContent(sessionId);
    } else if (selectedSession) {
      fetchChatContent(selectedSession.session_id);
    } else { // if its undefined - it's just new session
      setChatContent([]);
    }
  }, [sessionId, selectedSession, setChatContent, setShowCharacterSelection, setErrorMsg]);

  // scroll to bottom
  useEffect(() => {
    if (config.VERBOSE_SUPERB === 0) {
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
        {chatContent[currentSessionIndex] ? chatContent[currentSessionIndex].messages.map((message, index) => (
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
          : null
        }
        <div ref={endOfMessagesRef} />
      </div>
    </div>
  );
};

export default ChatWindow;
