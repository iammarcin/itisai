// utils/local.storage.js

const TTS_MODEL_KEY = 'ttsModel';
const STREAMING_KEY = 'streaming';
const AUTO_TRIGGER_TTS_KEY = 'autoTriggerTTS';
const VOICE_KEY = 'voice';
const SPEED_KEY = 'speed';
const ENV_KEY = 'selectedEnvironment';

export const getEnvironment = () => {
 return localStorage.getItem(ENV_KEY) || 'prod';
};

export const setEnvironment = (env) => {
 localStorage.setItem(ENV_KEY, env);
};

export const getTTSModel = () => {
 return localStorage.getItem(TTS_MODEL_KEY) || 'tts-1';
};

export const setTTSModel = (model) => {
 localStorage.setItem(TTS_MODEL_KEY, model);
};

export const getStreaming = () => {
 return JSON.parse(localStorage.getItem(STREAMING_KEY)) || false;
};

export const setStreaming = (streaming) => {
 localStorage.setItem(STREAMING_KEY, JSON.stringify(streaming));
};

export const getAutoTriggerTTS = () => {
 return JSON.parse(localStorage.getItem(AUTO_TRIGGER_TTS_KEY)) || false;
};

export const setAutoTriggerTTS = (autoTrigger) => {
 localStorage.setItem(AUTO_TRIGGER_TTS_KEY, JSON.stringify(autoTrigger));
};

export const getVoice = () => {
 return localStorage.getItem(VOICE_KEY) || 'shimmer';
};

export const setVoice = (voice) => {
 localStorage.setItem(VOICE_KEY, voice);
};

export const getSpeed = () => {
 return localStorage.getItem(SPEED_KEY) || '1.0';
};

export const setSpeed = (speed) => {
 localStorage.setItem(SPEED_KEY, speed);
};
