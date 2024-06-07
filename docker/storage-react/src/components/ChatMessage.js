// ChatMessage.js
import React, { useEffect } from 'react';
import './ChatMessage.css'; // Assuming you have CSS for chat messages
import Markdown from 'react-markdown';

const ChatMessage = ({ message }) => {
  useEffect(() => {
    console.log("Chat message:", message);
  }, [message]);

  const avatarSrc = message.isUserMessage 
    ? '/imgs/UserAvatar.png' 
    : `/imgs/${message.aiCharacterName}.png`;

  return (
    <div className={`chat-message ${message.isUserMessage ? 'user' : 'ai'}`}>
      <div className="avatar">
        <img src={avatarSrc} alt={message.isUserMessage ? 'User Avatar' : message.aiCharacterName} />
      </div>
      <div className="message-content">
        <p><Markdown>{message.message}</Markdown></p>
        {message.imageLocations && message.imageLocations.map((src, index) => (
          <img key={index} src={src} alt="Chat resource" />
        ))}
        {message.fileNames && message.fileNames.map((src, index) => (
          <audio key={index} controls>
            <source src={src} type="audio/ogg" />
            Your browser does not support the audio element.
          </audio>
        ))}
      </div>
    </div>
  );
};

export default ChatMessage;
