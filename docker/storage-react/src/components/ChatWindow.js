// ChatWindow.js
import React, { useEffect, useState } from 'react';
import ChatMessage from './ChatMessage';
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

  if (!selectedSession) {
    return <div className="chat-window">Select a chat session to view messages</div>;
  }

  return (
    <div className="chat-window">
      <div className="messages">
        {chatContent && chatContent.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}
      </div>
    </div>
  );
};

export default ChatWindow;
