// ChatMessage.js
import React, { useState, useEffect, useRef } from 'react';
import ChatImageModal from './ChatImageModal';
import './css/ChatMessage.css';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';

import { getTextAICharacter } from '../utils/configuration';
import apiMethods from '../services/api.methods';

// TODO MOVE TO CONFIG LATER
const ERROR_MESSAGE_FOR_TEXT_GEN = "Error in Text Generator. Try again!";

const ChatMessage = ({ index, message, isLastMessage, isUserMessage, contextMenuIndex, setContextMenuIndex, currentSessionIndex, currentSessionId, setCurrentSessionId, chatContent, setChatContent, setAttachedImages, setEditingMessage, setUserInput, setFocusInput, manageProgressText, setReadyForRegenerate, setErrorMsg }) => {
  const [contextMenu, setContextMenu] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const messageRef = useRef(null);
  const avatarSrc = message.isUserMessage
    ? '/imgs/UserAvatar.jpg'
    : `/imgs/${message.aiCharacterName}.png`;
  // set section for images and filter out placeholders
  const [validImageLocations, setValidImageLocations] = useState(
    message.imageLocations ? message.imageLocations.filter(src => src !== "image_placeholder_url") : []
  );

  // Update validImageLocations when message.imageLocations changes (for example when it's auto generated image)
  useEffect(() => {
    setValidImageLocations(
      message.imageLocations ? message.imageLocations.filter(src => src !== "image_placeholder_url") : []
    );
  }, [message.imageLocations]);

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
    // save message index (so we know which message was edited) and messageId from DB - so we can update it later in DB as well
    setEditingMessage({ index, messageId: message.messageId });
    console.log("imageLocations", message.imageLocations);
    setUserInput(message.message);
    setAttachedImages(message.imageLocations);
    setFocusInput(true);
    setContextMenu(null);
  };

  const handleRegenerate = () => {
    if (index > 0) {
      const previousMessage = chatContent[currentSessionIndex].messages[index - 1];

      // Check if the previous message is a user message
      if (previousMessage.isUserMessage) {
        console.log("previousMessage: ", previousMessage);
        setUserInput(previousMessage.message);
        //const attachedFiles = previousMessage.fileNames;
        setAttachedImages(previousMessage.imageLocations);
        // Set the editing message position
        setEditingMessage({ index: index - 1, messageId: previousMessage.messageId });

        setReadyForRegenerate(true);
      }
    }
    setContextMenu(null);
  };

  const handleNewSessionFromHere = () => {
    // Extract messages up to and including the specified index
    const selectedChatItems = chatContent[currentSessionIndex].messages.slice(0, index + 1).map(item => ({ ...item, messageId: null }));

    const updatedChatContent = [...chatContent];
    // preserve same character
    updatedChatContent[currentSessionIndex].ai_character_name = chatContent[currentSessionIndex].ai_character_name;
    updatedChatContent[currentSessionIndex].sessionId = ''; // New session will get a new ID from the backend
    updatedChatContent[currentSessionIndex].messages = selectedChatItems;
    setChatContent(updatedChatContent);

    setCurrentSessionId(null);

    setContextMenu(null);
  };

  const handleRemove = () => {
    // Remove the chat item
    const updatedChatContent = [...chatContent];
    const sessionMessages = updatedChatContent[currentSessionIndex].messages;

    sessionMessages.splice(index, 1);
    setChatContent(updatedChatContent);
    setContextMenu(null);

    // if next message is AI message - we should remove it too
    if (index < sessionMessages.length && !sessionMessages[index].isUserMessage) {
      sessionMessages.splice(index, 1);
      setChatContent(updatedChatContent);
    }

    // Check if session is empty
    const dbMethodToExecute = sessionMessages.length === 0 ? "db_remove_session" : "db_update_session";

    const finalInputForDB = {
      session_id: currentSessionId,
      chat_history: sessionMessages.map(msg => ({ ...msg, messageId: msg.messageId || "" }))
    };

    if (dbMethodToExecute === "db_remove_session") {
      apiMethods.triggerAPIRequest("api/db", "provider.db", "db_remove_session", finalInputForDB);
    } else {
      apiMethods.updateSessionInDB(updatedChatContent[currentSessionIndex], currentSessionId);
    }
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
        {isUserMessage && !isLastMessage && (
          <div className="context-menu-item" onClick={handleRemove}>Remove</div>
        )}
        {!isUserMessage && (
          <>
            {isLastMessage && (
              <div className="context-menu-item" onClick={handleRegenerate}>Regenerate</div>
            )}
          </>
        )}
        <div className="context-menu-item" onClick={handleNewSessionFromHere}>New Session from here</div>
        <div className="context-menu-item" onClick={handleCopy}>Copy</div>
      </div>
    );
  };

  // IMAGE MODAL
  const handleImageClick = (index) => {
    setCurrentImageIndex(index);
    setIsModalOpen(true);
  };
  const handleCloseModal = () => {
    setIsModalOpen(false);
  };
  const handleNextImage = () => {
    setCurrentImageIndex((prevIndex) => (prevIndex + 1) % validImageLocations.length);
  };
  const handlePrevImage = () => {
    setCurrentImageIndex((prevIndex) => (prevIndex - 1 + validImageLocations.length) % validImageLocations.length);
  };

  const handleImgGenClick = async () => {
    try {
      manageProgressText("show", "Image");
      const imageLocation = await apiMethods.generateImage(message.message);
      if (imageLocation) {
        setValidImageLocations(prevLocations => [...prevLocations, imageLocation]);
        // update chat content
        setChatContent((prevChatContent) => {
          // Make sure we update the correct session
          const updatedContent = [...prevChatContent];
          const sessionMessages = updatedContent[currentSessionIndex].messages;
          const currentMessage = sessionMessages[index];

          if (!currentMessage.imageLocations.includes(imageLocation)) {
            currentMessage.imageLocations.push(imageLocation);
          }
          // save to DB - i had to do it here - because if it was out of setChatContent - it sent outdated data
          apiMethods.updateSessionInDB(updatedContent[currentSessionIndex], currentSessionId);
          return updatedContent;
        });
      } else {
        throw new Error("Problem generating image");
      }
    } catch (error) {
      setErrorMsg(error);
      console.error(error);
    } finally {
      manageProgressText("hide", "Image");
    }
  }

  const handleLocationClick = () => {
    if (message.message.startsWith("GPS location:")) {
      const coordinates = message.message.replace("GPS location:", "").trim();
      const googleMapsUrl = `https://www.google.com/maps?q=${coordinates}`;
      window.open(googleMapsUrl, '_blank');
    }
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
        {getTextAICharacter() === 'tools_artgen' && !message.isUserMessage ? (
          <button className="img-chat-message-button" onClick={handleImgGenClick}>
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h560v-560H200v560Zm40-80h480L570-480 450-320l-90-120-120 160Zm-40 80v-560 560Z" /></svg>
          </button>
        ) : null}
        {message.isGPSLocationMessage ? (
          <button className="img-chat-message-button" onClick={handleLocationClick}>
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M480-480q33 0 56.5-23.5T560-560q0-33-23.5-56.5T480-640q-33 0-56.5 23.5T400-560q0 33 23.5 56.5T480-480Zm0 294q122-112 181-203.5T720-552q0-109-69.5-178.5T480-800q-101 0-170.5 69.5T240-552q0 71 59 162.5T480-186Zm0 106Q319-217 239.5-334.5T160-552q0-150 96.5-239T480-880q127 0 223.5 89T800-552q0 100-79.5 217.5T480-80Zm0-480Z" /></svg>
          </button>
        ) : null}
        {validImageLocations.length > 0 && (
          <div className="image-container">
            {validImageLocations.map((src, index) => (
              <img key={index} src={src} alt="Chat" onClick={() => handleImageClick(index)} />
            ))}
          </div>
        )}
        {message.fileNames && message.fileNames.map((src, index) => (
          <audio key={index} controls>
            <source src={src} type="audio/ogg" />
            Your browser does not support the audio element.
          </audio>
        ))}
      </div>
      {
        isModalOpen && (
          <ChatImageModal
            images={validImageLocations}
            currentIndex={currentImageIndex}
            onClose={handleCloseModal}
            onNext={handleNextImage}
            onPrev={handlePrevImage}
          />
        )
      }
    </div >
  );
};

export default ChatMessage;
