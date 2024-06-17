import React, { useState } from 'react';
import './css/OptionsWindow.css';

const OptionsWindow = () => {
 const [activeOption, setActiveOption] = useState('GENERAL');

 const options = ['GENERAL', 'TEXT', 'IMAGE', 'TTS', 'SPEECH'];

 const renderContent = () => {
  switch (activeOption) {
   case 'GENERAL':
    return <p>GENERAL</p>;
   case 'TEXT':
    return <p>TEXT</p>;
   case 'IMAGE':
    return <p>IMAGE</p>;
   case 'TTS':
    return <p>TTS</p>;
   case 'SPEECH':
    return <p>SPEECH</p>;
   default:
    return <p>GENERAL</p>;
  }
 };

 return (
  <div className="options-window">
   <div className="options-menu">
    {options.map(option => (
     <button
      key={option}
      className={`options-button ${activeOption === option ? 'active' : ''}`}
      onClick={() => setActiveOption(option)}
     >
      {option}
     </button>
    ))}
   </div>
   <div className="options-content">
    {renderContent()}
   </div>
  </div>
 );
};

export default OptionsWindow;
