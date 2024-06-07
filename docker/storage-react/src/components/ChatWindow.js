// ChatWindow.js
import React, { useEffect, useState } from 'react';
import ChatMessage from './ChatMessage';
import apiService from '../services/apiService';
import './ChatWindow.css'; // Assuming you have CSS for chat window

const ChatWindow = ({ selectedSession }) => {
  const [chatContent, setChatContent] = useState(null);

  useEffect(() => {
    if (selectedSession) {
      const fetchChatContent = async () => {
        try {
          const content = await apiService.fetchChatContent(selectedSession.session_id);
          console.log("Chat content:", content);
          setChatContent(content);
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
      <h2>{selectedSession.session_name}</h2>
      <div className="messages">
        {chatContent && chatContent.map((message, index) => (
          <ChatMessage key={index} message={message} />
        ))}
      </div>
    </div>
  );
};

export default ChatWindow;
