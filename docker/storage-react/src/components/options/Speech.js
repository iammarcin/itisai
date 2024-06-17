// options/Speech.js

import React from 'react';

const Speech = () => {
 return (
  <div className="tts-options">
   <div className="option-item">
    <label>Language</label>
    <input type="text" value="en" />
   </div>
   <div className="option-item">
    <label>Temperature</label>
    <input type="range" min="0" max="1" step="0.05" />
    <span>1.0</span>
   </div>
  </div>
 );
};

export default Speech;
