// options/Text.js

import React, { useState } from 'react';
import {
 getTextTemperature, setTextTemperature,
 getTextMemorySize, setTextMemorySize,
 getIsStreamingEnabled, setIsStreamingEnabled
} from '../../utils/configuration';

const Text = () => {
 const [temperature, setLocalTemperature] = useState(getTextTemperature());
 const [memorySize, setLocalMemorySize] = useState(getTextMemorySize());
 const [isStreaming, setLocalIsStreaming] = useState(getIsStreamingEnabled());

 const handleTemperatureChange = (e) => {
  const value = e.target.value;
  setLocalTemperature(value);
  setTextTemperature(value);
 };

 const handleMemorySizeChange = (e) => {
  const value = e.target.value;
  setLocalMemorySize(value);
  setTextMemorySize(value);
 };

 const handleStreamingChange = (e) => {
  const checked = e.target.checked;
  setLocalIsStreaming(checked);
  setIsStreamingEnabled(checked);
 };

 return (
  <div className="text-options">
   <div className="option-item">
    <label>Temperature</label>
    <input
     type="range"
     min="0"
     max="1"
     step="0.05"
     value={temperature}
     onChange={handleTemperatureChange}
    />
    <span>{temperature}</span>
   </div>
   <div className="option-item">
    <label>Memory Size</label>
    <input
     type="range"
     min="0"
     max="2000"
     step="1"
     value={memorySize}
     onChange={handleMemorySizeChange}
    />
    <span>{memorySize}</span>
   </div>
   <div className="option-item">
    <label>Streaming</label>
    <input
     type="checkbox"
     checked={isStreaming}
     onChange={handleStreamingChange}
    />
   </div>
  </div>
 );
};

export default Text;
