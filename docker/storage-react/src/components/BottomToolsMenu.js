// BottomToolsMenu.js
import React, { useState, useRef, useEffect } from 'react';
import './css/BottomToolsMenu.css';
import apiMethods from '../services/api.methods';
import ChatCharacters, { filterCharacters, characters } from './ChatCharacters';

import { getTextAICharacter, setTextAICharacter, setOriginalAICharacter } from '../utils/configuration';

import { resizeImage } from '../utils/image.utils';

const BottomToolsMenu = ({ userInput, setUserInput, attachedImages, setAttachedImages, handleSendClick, focusInput, setFocusInput, isLoading, setErrorMsg }) => {
  const userInputRef = useRef(null);
  // to control UI while images are being uploaded
  const [uploading, setUploading] = useState(false);
  const [showLocalCharacterSelect, setShowLocalCharacterSelect] = useState(false);
  // used when choosing character after @ is used
  const [displayedCharacters, setDisplayedCharacters] = useState(characters);
  // when filtering characters - one will be selected by default - this was done because when hitting enter (when character select view was visible) it was submitting message and not choosing character
  const [selectedCharacterName, setSelectedCharacterName] = useState("Assistant");

  const handleSendButtonClick = () => {
    setShowLocalCharacterSelect(false);
    handleSendClick();
  }

  const handleAttachClick = () => {
    document.getElementById('file-input').click();
  };

  const handleFileChange = async (e) => {
    setErrorMsg("");
    const files = Array.from(e.target.files);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));

    // Display placeholders
    const placeholders = imageFiles.map(file => ({ file, url: '', placeholder: true }));
    setAttachedImages(prevImages => [...prevImages, ...placeholders]);

    setUploading(true);
    for (const imageFile of imageFiles) {
      try {
        const resizedFile = await resizeImage(imageFile);
        const response = await apiMethods.uploadFileToS3("api/aws", "provider.s3", "s3_upload", resizedFile);

        if (response.success) {
          const newUrl = response.message.result;
          setAttachedImages(prevImages => prevImages.map(img => img.file === imageFile ? { ...img, url: newUrl, placeholder: false } : img));
        } else {
          setErrorMsg("Problem with file upload. Try again.")
          throw new Error(response.message);
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        setErrorMsg("Problem with file upload. Try again.")
        setAttachedImages(prevImages => prevImages.filter(img => img.file !== imageFile));
      }
    }
    setUploading(false);
  };

  const handleRemoveImage = (index) => {
    setAttachedImages(prevImages => prevImages.filter((_, i) => i !== index));
  };

  const handleInputChange = (e) => {
    const inputValue = e.target.value;
    setUserInput(inputValue);

    // if @ is used - we trigger character selection view
    if (inputValue.includes("@")) {
      const atIndex = inputValue.lastIndexOf("@");
      const query = inputValue.substring(atIndex + 1).toLowerCase();
      // we can filter out characters by name
      if (query === "") {
        setDisplayedCharacters(characters);
      } else {
        const filtered = filterCharacters(query);
        setDisplayedCharacters(filtered);
      }
    } else { // if there is @ in userInput (for example removed) - hide selection view
      setShowLocalCharacterSelect(false);
    }

    if (inputValue === "") {
      setShowLocalCharacterSelect(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendClick();
    }
  };

  // to handle ENTER, arrows (when choosing AI character from the list)
  const handleKeyDown = async (event) => {
    if (showLocalCharacterSelect) {
      var currentIndex = displayedCharacters.findIndex(char => char.name === selectedCharacterName);
      // there were some stupid problems - where currentIndex was found as -1
      if (displayedCharacters.length === 1) currentIndex = 0;

      if (event.key === "Enter" || event.key === 13) {
        event.preventDefault();
        handleCharacterSelect(displayedCharacters[currentIndex]);
      } else if (event.key === "ArrowRight" || event.key === 39) {
        event.preventDefault();
        const nextIndex = (currentIndex + 1) % displayedCharacters.length;
        setSelectedCharacterName(displayedCharacters[nextIndex].name);
      } else if (event.key === "ArrowLeft" || event.key === 37) {
        event.preventDefault();
        const prevIndex = (currentIndex - 1 + displayedCharacters.length) % displayedCharacters.length;
        setSelectedCharacterName(displayedCharacters[prevIndex].name);
      } else if (event.key === "Escape" || event.key === 27) {
        setShowLocalCharacterSelect(false);
      }
    } else if (event.key === "@" || event.key === 50) {
      setShowLocalCharacterSelect(true);
    }
  };

  // executed when character is chosen from the list
  const handleCharacterSelect = (character) => {
    setShowLocalCharacterSelect(false);
    // set current (main AI character) to temporary variable (so later in ChatHandleAPI we can fallback)
    setOriginalAICharacter(getTextAICharacter());
    // and temporarily set chosen character as main AI character
    setTextAICharacter(character.nameForAPI);
    // reset display character (for next execution)
    setDisplayedCharacters(characters);
    // set nicely full name of AI character after @
    setUserInput((prevInput) => {
      const cursorPosition = userInputRef.current.selectionStart;
      const atIndex = prevInput.lastIndexOf("@", cursorPosition - 1);
      if (atIndex !== -1) {
        const newText = prevInput.substring(0, atIndex + 1) + character.name + " " + prevInput.substring(cursorPosition);
        return newText;
      }
      return prevInput;
    });
  };

  // setting height of user input (if more then 1 line)
  useEffect(() => {
    const input = userInputRef.current;
    if (input) {
      input.style.height = 'auto';
      input.style.height = `${Math.min(input.scrollHeight, 100)}px`;
    }
  }, [userInput]);

  // make sure that user input is active on load (so we will not need to click on it)
  useEffect(() => {
    if (userInputRef.current) {
      userInputRef.current.focus();
    }
  }, []);
  useEffect(() => {
    if (focusInput && userInputRef.current) {
      userInputRef.current.focus();
      setFocusInput(false);
    }
  }, [focusInput, setFocusInput]);

  return (
    <div className="bottom-tools-menu">
      <div className="bottom-tools-menu-characters">
        {showLocalCharacterSelect && <ChatCharacters onSelect={handleCharacterSelect} characters={displayedCharacters} selectedCharacterName={selectedCharacterName} />}
      </div>
      <div className="image-preview-container">
        {attachedImages.map((image, index) => (
          <div key={index} className="image-preview">
            {image.placeholder ? (
              <div className="placeholder" />
            ) : (
              <img src={image.url} alt="preview" />
            )}
            <button className="remove-button" onClick={() => handleRemoveImage(index)}>X</button>
          </div>
        ))}
      </div>
      <div className="input-container">
        <textarea
          ref={userInputRef}
          className="message-input"
          placeholder="Talk to me..."
          value={userInput}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={isLoading}
        />
        <div className="button-container">
          <button className="send-button" onClick={handleSendButtonClick} disabled={isLoading || uploading}>
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M120-160v-640l760 320-760 320Zm80-120 474-200-474-200v140l240 60-240 60v140Zm0 0v-400 400Z" /></svg>
          </button>
          <button className="attach-button" onClick={handleAttachClick} disabled={isLoading || uploading}>
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M720-330q0 104-73 177T470-80q-104 0-177-73t-73-177v-370q0-75 52.5-127.5T400-880q75 0 127.5 52.5T580-700v350q0 46-32 78t-78 32q-46 0-78-32t-32-78v-370h80v370q0 13 8.5 21.5T470-320q13 0 21.5-8.5T500-350v-350q-1-42-29.5-71T400-800q-42 0-71 29t-29 71v370q-1 71 49 120.5T470-160q70 0 119-49.5T640-330v-390h80v390Z" /></svg>
          </button>
        </div>
      </div>
      <input
        type="file"
        id="file-input"
        style={{ display: 'none' }}
        onChange={handleFileChange}
        accept="image/*"
        multiple
      />
    </div>
  );
};

export default BottomToolsMenu;
