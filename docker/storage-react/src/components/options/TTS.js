// options/TTS.js

import React, { useState } from 'react';
import { setTTSModel, getTTSModel, setStreaming, getStreaming, setAutoTriggerTTS, getAutoTriggerTTS, setVoice, getVoice, setSpeed, getSpeed } from '../../utils/local.storage';

const TTS = () => {
 const [ttsModel, setLocalTTSModel] = useState(getTTSModel());
 const [streaming, setLocalStreaming] = useState(getStreaming());
 const [autoTriggerTTS, setLocalAutoTriggerTTS] = useState(getAutoTriggerTTS());
 const [voice, setLocalVoice] = useState(getVoice());
 const [speed, setLocalSpeed] = useState(getSpeed());

 const handleModelChange = (e) => {
  const value = e.target.value;
  setLocalTTSModel(value);
  setTTSModel(value);
 };

 const handleStreamingChange = (e) => {
  const checked = e.target.checked;
  setLocalStreaming(checked);
  setStreaming(checked);
 };

 const handleAutoTriggerTTSChange = (e) => {
  const checked = e.target.checked;
  setLocalAutoTriggerTTS(checked);
  setAutoTriggerTTS(checked);
 };

 const handleVoiceChange = (e) => {
  const value = e.target.value;
  setLocalVoice(value);
  setVoice(value);
 };

 const handleSpeedChange = (e) => {
  const value = e.target.value;
  setLocalSpeed(value);
  setSpeed(value);
 };

 return (
  <div className="tts-options">
   <div className="option-item">
    <label>Model</label>
    <input type="text" value={ttsModel} onChange={handleModelChange} />
   </div>
   <div className="optionsAdditionalText">Possible values: tts-1, tts-1-hd</div>
   <div className="option-item">
    <label>Streaming</label>
    <input type="checkbox" checked={streaming} onChange={handleStreamingChange} />
   </div>
   <div className="option-item">
    <label>Auto trigger TTS upon AI response</label>
    <input type="checkbox" checked={autoTriggerTTS} onChange={handleAutoTriggerTTSChange} />
   </div>
   <h3>OpenAI</h3>
   <div className="option-item">
    <label>Voice</label>
    <input type="text" value={voice} onChange={handleVoiceChange} />
   </div>
   <div className="optionsAdditionalText">Possible values: alloy, echo, fable, onyx, nova, and shimmer</div>
   <div className="option-item">
    <label>Speed</label>
    <input type="range" min="0.5" max="4" step="0.05" value={speed} onChange={handleSpeedChange} />
    <span>{speed}</span>
   </div>
  </div>
 );
};

export default TTS;
