// options/Text.js

import React from 'react';

const Text = () => {
 return (
  <div className="text-options">
   <div className="option-item">
    <label>Temperature</label>
    <input type="range" min="0" max="1" step="0.05" />
    <span>0.15</span>
   </div>
   <div className="option-item">
    <label>Memory Size</label>
    <input type="range" min="0" max="2000" step="1" />
    <span>1578.0</span>
   </div>
   <div className="option-item">
    <label>Streaming</label>
    <input type="checkbox" />
   </div>
  </div>
 );
};

export default Text;
