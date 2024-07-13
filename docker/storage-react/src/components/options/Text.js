// options/Text.js

import React, { useState } from 'react';
import {
  getTextTemperature, setTextTemperature,
  getTextMemorySize, setTextMemorySize,
  getTextFileAttachedMessageLimit, setTextFileAttachedMessageLimit,
  getIsStreamingEnabled, setIsStreamingEnabled
} from '../../utils/configuration';

const Text = () => {
  const [temperature, setLocalTemperature] = useState(getTextTemperature());
  const [memorySize, setLocalMemorySize] = useState(getTextMemorySize());
  const [fileAttachedMessageLimit, setLocalFileAttachedMessageLimit] = useState(getTextFileAttachedMessageLimit());
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

  const handleFileAttachedMessageLimitChange = (e) => {
    const value = e.target.value;
    setLocalFileAttachedMessageLimit(value);
    setTextFileAttachedMessageLimit(value);
  }

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
        <label>Attachments message count limit</label>
        <input
          type="range"
          min="0"
          max="10"
          step="1"
          value={fileAttachedMessageLimit}
          onChange={handleFileAttachedMessageLimitChange}
        />
        <span>{fileAttachedMessageLimit}</span>
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
