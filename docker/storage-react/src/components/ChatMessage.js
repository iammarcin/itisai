// ChatMessage.js
import React from 'react';
import './ChatMessage.css';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatMessage = ({ message }) => {
  const avatarSrc = message.isUserMessage 
    ? '/imgs/UserAvatar.png' 
    : `/imgs/${message.aiCharacterName}.png`;

    return (
      <div className={`chat-message ${message.isUserMessage ? 'user' : 'ai'}`}>
        <div className="avatar">
          <img src={avatarSrc} alt={message.isUserMessage ? 'User Avatar' : message.aiCharacterName} />
        </div>
        <div className="message-content">
          <Markdown
            children={message.message}
            remarkPlugins={[remarkGfm]}
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
