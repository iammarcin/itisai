// BottomToolsMenu.js
import React, { useState, useRef, useEffect } from 'react';
import './css/BottomToolsMenu.css';

const BottomToolsMenu = ({ userInput, setUserInput, callChatAPI, isLoading }) => {
 const [images, setImages] = useState([]);
 const userInputRef = useRef(null);

 const handleSendClick = () => {
  setUserInput("")
  callChatAPI(userInput);
 };

 const handleAttachClick = () => {
  document.getElementById('file-input').click();
 };

 const handleFileChange = (e) => {
  const files = Array.from(e.target.files);
  const imageFiles = files.filter(file => file.type.startsWith('image/'));
  setImages(prevImages => [...prevImages, ...imageFiles]);
 };

 const handleRemoveImage = (index) => {
  setImages(prevImages => prevImages.filter((_, i) => i !== index));
 };

 const handleInputChange = (e) => {
  setUserInput(e.target.value);
 };

 const handleKeyPress = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
   e.preventDefault();
   handleSendClick();
  }
 };

 // setting height of user input (if more then 1 line)
 useEffect(() => {
  const input = userInputRef.current;
  if (input) {
   input.style.height = 'auto';
   input.style.height = `${Math.min(input.scrollHeight, 100)}px`;
  }
 }, [userInput]);

 return (
  <div className="bottom-tools-menu">
   <div className="image-preview-container">
    {images.map((image, index) => (
     <div key={index} className="image-preview">
      <img src={URL.createObjectURL(image)} alt="preview" />
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
     rows={1}
     disabled={isLoading}
    />
    <div className="button-container">
     <button className="send-button" onClick={handleSendClick} disabled={isLoading}>
      <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M120-160v-640l760 320-760 320Zm80-120 474-200-474-200v140l240 60-240 60v140Zm0 0v-400 400Z" /></svg>
     </button>
     <button className="attach-button" onClick={handleAttachClick}>
      <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M720-330q0 104-73 177T470-80q-104 0-177-73t-73-177v-370q0-75 52.5-127.5T400-880q75 0 127.5 52.5T580-700v350q0 46-32 78t-78 32q-46 0-78-32t-32-78v-370h80v370q0 13 8.5 21.5T470-320q13 0 21.5-8.5T500-350v-350q-1-42-29.5-71T400-800q-42 0-71 29t-29 71v370q-1 71 49 120.5T470-160q70 0 119-49.5T640-330v-390h80v390Z" /></svg>
     </button>
    </div>
   </div>
   <input
    type="file"
    id="file-input"
    style={{ display: 'none' }}
    onChange={handleFileChange}
    accept="image/*,audio/*"
    multiple
   />
  </div>
 );
};

export default BottomToolsMenu;
