// options/Image.js

import React, { useState } from 'react';
import {
 getImageModelName,
 getImageQualityHD, setImageQualityHD,
 getImageDisableSafePrompt, setImageDisableSafePrompt,
 getImageArtgenShowPrompt, setImageArtgenShowPrompt,
 getImageAutoGenerateImage, setImageAutoGenerateImage
} from '../../utils/configuration';

const Image = () => {
 const [model, setModel] = useState(getImageModelName());
 const [qualityHD, setQualityHD] = useState(getImageQualityHD());
 const [disableSafePrompt, setDisableSafePrompt] = useState(getImageDisableSafePrompt());
 const [showPrompt, setShowPrompt] = useState(getImageArtgenShowPrompt());
 const [autoGenerateImage, setAutoGenerateImage] = useState(getImageAutoGenerateImage());

 const handleModelChange = (e) => {
  const value = e.target.value;
  setModel(value);
 }

 const handleQualityHDChange = (e) => {
  const checked = e.target.checked;
  setQualityHD(checked);
  setImageQualityHD(checked);
 };

 const handleDisableSafePromptChange = (e) => {
  const checked = e.target.checked;
  setDisableSafePrompt(checked);
  setImageDisableSafePrompt(checked);
 };

 const handleShowPromptChange = (e) => {
  const checked = e.target.checked;
  setShowPrompt(checked);
  setImageArtgenShowPrompt(checked);
 };

 const handleAutoGenerateImageChange = (e) => {
  const checked = e.target.checked;
  setAutoGenerateImage(checked);
  setImageAutoGenerateImage(checked);
 };

 return (
  <div className="image-options">
   <div className="option-item">
    <label>Model</label>
    <input type="text" value={model} readOnly onChange={handleModelChange} />
   </div>
   <div className="optionsAdditionalText">Possible values: dall-e-3</div>
   <div className="option-item">
    <label>HD Quality</label>
    <input type="checkbox" checked={qualityHD} onChange={handleQualityHDChange} />
   </div>
   <div className="option-item">
    <label>Disable Openai revised prompt</label>
    <input type="checkbox" checked={disableSafePrompt} onChange={handleDisableSafePromptChange} />
   </div>
   <h3>Artgen mode</h3>
   <div className="option-item">
    <label>Show image prompt</label>
    <input type="checkbox" checked={showPrompt} onChange={handleShowPromptChange} />
   </div>
   <div className="option-item">
    <label>Auto generate image</label>
    <input type="checkbox" checked={autoGenerateImage} onChange={handleAutoGenerateImageChange} />
   </div>
  </div>
 );
};

export default Image;
