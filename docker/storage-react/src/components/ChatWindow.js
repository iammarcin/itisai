// ChatWindow.js
import React, { useEffect, useState } from 'react';
import ChatMessage from './ChatMessage';
import ChatCharacters from './ChatCharacters';
import apiMethods from '../services/api.methods';
import './css/ChatWindow.css';

const ChatWindow = ({ selectedSession }) => {
  const [chatContent, setChatContent] = useState(null);

  useEffect(() => {
    if (selectedSession) {
      const fetchChatContent = async () => {
        try {
          const userInput = { "session_id": selectedSession.session_id };
          const response = await apiMethods.triggerAPIRequest("db", "provider.db", "db_get_user_session", userInput);

          const chatHistory = JSON.parse(response.message.result.chat_history);

          setChatContent(Array.isArray(chatHistory) ? chatHistory : []);

        } catch (error) {
          console.error('Failed to fetch chat content', error);
        }
      };

      fetchChatContent();
    }
  }, [selectedSession]);

  const handleCharacterSelect = (character) => {
    console.log(`Selected character: ${character.name}`);
    // Add logic to handle character selection, e.g., start a new session
  };

  return (
    <div className="chat-window">
      {!selectedSession ? (
        <ChatCharacters onSelect={handleCharacterSelect} />
      ) : (
        <div className="messages">
          {chatContent && chatContent.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
