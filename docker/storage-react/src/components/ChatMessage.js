// ChatMessage.js
import React from 'react';
import './ChatMessage.css';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';

// TODO MOVE TO CONFIG LATER
const ERROR_MESSAGE_FOR_TEXT_GEN = "Error in Text Generator. Try again!";


const ChatMessage = ({ message }) => {
  const avatarSrc = message.isUserMessage 
    ? '/imgs/UserAvatar.png' 
    : `/imgs/${message.aiCharacterName}.png`;

  // filter out placeholders
  const validImageLocations = message.imageLocations 
    ? message.imageLocations.filter(src => src !== "image_placeholder_url") 
    : [];

  // Check if message is empty and imageLocations and fileNames are also empty
  if ((message.message === "" || message.message === ERROR_MESSAGE_FOR_TEXT_GEN) && validImageLocations.length === 0 && (!message.fileNames || message.fileNames.length === 0)) {
    return null;
  }
  // if message is empty, but files are present - it means that it is attached audio file or recording that was transcribed... so we don't need it
  if (message.message === "" && message.fileNames && message.fileNames.length > 0) {
    return null;
  }

  return (
    <div className={`chat-message ${message.isUserMessage ? 'user' : 'ai'}`}>
      <div className="avatar">
        <img src={avatarSrc} alt="avatar"/>
      </div>
      <div className="message-content">
        <Markdown
          children={message.message}
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight]}
          components={{
            p: ({ node, ...props }) => {
              const hasImage = node.children.some(child => child.tagName === 'img');
              if (hasImage) return <div {...props} />;
              return <p {...props} />;
            },
            pre: ({ node, ...props }) => <pre {...props} />,
            code: ({ node, ...props }) => <code {...props} />
          }}
        />
        {validImageLocations.map((src, index) => (
        <img key={index} src={src} alt="Chat"/>
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
