// ChatMessage.js
import React, { useState, useEffect, useRef } from 'react';
import './css/ChatMessage.css';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';

// TODO MOVE TO CONFIG LATER
const ERROR_MESSAGE_FOR_TEXT_GEN = "Error in Text Generator. Try again!";


const ChatMessage = ({ message, index, isLastMessage, isUserMessage, contextMenuIndex, setContextMenuIndex }) => {
  const [contextMenu, setContextMenu] = useState(null);
  const messageRef = useRef(null);
  const avatarSrc = message.isUserMessage
    ? '/imgs/UserAvatar.jpg'
    : `/imgs/${message.aiCharacterName}.png`;

  // filter out placeholders
  const validImageLocations = message.imageLocations
    ? message.imageLocations.filter(src => src !== "image_placeholder_url")
    : [];

  // and listener for click outside (if context menu appears and we click somewhere else we want to hide it)
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (contextMenu && !event.target.closest('.context-menu')) {
        setContextMenu(null);
        setContextMenuIndex(null);
      }
    };

    document.addEventListener('click', handleClickOutside);

    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [contextMenu, setContextMenuIndex]);

  // Check if message is empty and imageLocations and fileNames are also empty
  if ((message.message === "" || message.message === ERROR_MESSAGE_FOR_TEXT_GEN) && validImageLocations.length === 0 && (!message.fileNames || message.fileNames.length === 0)) {
    return null;
  }

  // if message is empty, but files are present - it means that it is attached audio file or recording that was transcribed... so we don't need it
  if (message.message === "" && message.fileNames && message.fileNames.length > 0) {
    return null;
  }

  // show context menu when right clicked
  const handleRightClick = (event) => {
    event.preventDefault();
    setContextMenu(null);

    setContextMenu({
      x: event.clientX,
      y: event.clientY,
    });
    setContextMenuIndex(index);
  };

  const handleCopy = () => {
    if (process.env.NODE_ENV === 'production') {
      navigator.clipboard.writeText(message.message)
        .catch((error) => {
          console.error('Failed to copy message', error);
        });
    } else {
      const textarea = document.createElement('textarea');
      textarea.value = message.message;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
    }
    setContextMenu(null);
  };

  const handleEdit = () => {
    console.log('Edit message');
    setContextMenu(null);
  };

  const handleRegenerate = () => {
    console.log('Regenerate message');
    setContextMenu(null);
  };

  // show context menu (on right click) - different per user and ai message
  const renderContextMenu = () => {
    if (!contextMenu || contextMenuIndex !== index) return null;
    return (
      <div
        className="context-menu"
        style={{ top: contextMenu.y, left: contextMenu.x, position: 'fixed' }}
      >
        {isUserMessage && isLastMessage && (
          <div className="context-menu-item" onClick={handleEdit}>Edit</div>
        )}
        {!isUserMessage && (
          <>
            {isLastMessage && (
              <div className="context-menu-item" onClick={handleRegenerate}>Regenerate</div>
            )}
          </>
        )}
        <div className="context-menu-item" onClick={handleCopy}>Copy</div>
      </div>
    );
  };


  return (
    <div className={`chat-message ${message.isUserMessage ? 'user' : 'ai'}`}
      onContextMenu={handleRightClick}
      ref={messageRef}
    >
      {renderContextMenu()}
      <div className="avatar">
        <img src={avatarSrc} alt="avatar" />
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
          <img key={index} src={src} alt="Chat" />
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
