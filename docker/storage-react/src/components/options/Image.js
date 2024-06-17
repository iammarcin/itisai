// options/Image.js

import React from 'react';

const Image = () => {
 return (
  <div className="image-options">
   <div className="option-item">
    <label>Model</label>
    <input type="text" value="dall-e-3" readonly />
   </div>
   <div className="optionsAdditionalText">Possible values: dall-e-3</div>
   <div className="option-item">
    <label>HD Quality</label>
    <input type="checkbox" />
   </div>
   <div className="option-item">
    <label>Disable Openai revised prompt</label>
    <input type="checkbox" />
   </div>
   <h3>Artgen mode</h3>
   <div className="option-item">
    <label>Show image prompt</label>
    <input type="checkbox" />
   </div>
   <div className="option-item">
    <label>Auto generate image</label>
    <input type="checkbox" />
   </div>
  </div>
 );
};

export default Image;
