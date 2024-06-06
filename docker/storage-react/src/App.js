// App.js
import React, { useState, useEffect } from 'react';
import ChatList from './ChatList';
import ChatDisplay from './ChatDisplay';
import fetchChatData from './fetchChatData';
import './App.css';

const App = () => {
  const [chatSessions, setChatSessions] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);

  useEffect(() => {
    // Fetch the list of chat sessions from the server
    fetch('/api/chats') // Adjust the API endpoint as necessary
      .then(response => response.json())
      .then(data => setChatSessions(data))
      .catch(error => console.error('Error fetching chat sessions:', error));
  }, []);

  const handleChatSelect = (chatId) => {
    fetchChatData(chatId)
      .then(data => setSelectedChat(data))
      .catch(error => console.error('Error fetching chat data:', error));
  };

  return (
    <div className="App">
      <ChatList
        chatSessions={chatSessions}
        onChatSelect={handleChatSelect}
      />
      {selectedChat && <ChatDisplay chatData={selectedChat} />}
    </div>
  );
};

export default App;

