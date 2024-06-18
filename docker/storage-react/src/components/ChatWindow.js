// ChatWindow.js
import React, { useEffect, useState } from 'react';
import ChatMessage from './ChatMessage';
import ChatCharacters from './ChatCharacters';
import apiMethods from '../services/api.methods';
import './css/ChatWindow.css';

const ChatWindow = ({ sessionId, selectedSession, chatContent, setChatContent, showCharacterSelection, setShowCharacterSelection }) => {
  // if i right click on any message (to show context window) - we need to reset previous context window 
  // if i clicked 2 time on 2 diff messages - two diff context menu were shown
  const [contextMenuIndex, setContextMenuIndex] = useState(null);

  // fetch chat content (for specific session)
  useEffect(() => {
    const fetchChatContent = async (sessionIdToGet) => {
      try {
        const userInput = { "session_id": sessionIdToGet };
        const response = await apiMethods.triggerAPIRequest("api/db", "provider.db", "db_get_user_session", userInput);

        const chatHistory = JSON.parse(response.message.result.chat_history);

        setChatContent(Array.isArray(chatHistory) ? chatHistory : []);
        setShowCharacterSelection(false);
      } catch (error) {
        console.error('Failed to fetch chat content', error);
      }
    };

    if (sessionId) {
      fetchChatContent(sessionId);
    } else if (selectedSession) {
      fetchChatContent(selectedSession.session_id);
    } else { // if its undefined - it's just new session
      setChatContent(null);
    }
  }, [sessionId, selectedSession, setChatContent, setShowCharacterSelection]);

  const handleCharacterSelect = (character) => {
    console.log(`Selected character: ${character.name}`);
    setShowCharacterSelection(false)
    // Add logic to handle character selection, e.g., start a new session
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
        {chatContent && chatContent.map((message, index) => (
          <ChatMessage
            key={index}
            index={index}
            message={message}
            isLastMessage={isLastMessage(index, message)}
            isUserMessage={message.isUserMessage}
            contextMenuIndex={contextMenuIndex}
            setContextMenuIndex={setContextMenuIndex}
          />
        ))}
      </div>
    </div>
  );
};

export default ChatWindow;
