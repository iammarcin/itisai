// ChatMessage.js
import React from 'react';
import './ChatMessage.css'; // Assuming you have CSS for chat messages

const ChatMessage = ({ message }) => {
  return (
    <div className={`chat-message ${message.isUserMessage ? 'user' : 'ai'}`}>
      <p>{message.message}</p>
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
  );
};

export default ChatMessage;
