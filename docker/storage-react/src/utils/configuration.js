// utils/configuration.js

// Keys
const APP_MODE_PRODUCTION = "app_mode_production";
const APP_MODE_API_URL = "app_mode_api_url";
const APP_MODE_USE_WATSON = "app_mode_use_watson";
const TEXT_MODEL_NAME = "text_model_name";
const TEXT_TEMPERATURE = "text_temperature";
const TEXT_MEMORY_SIZE = "text_memory_size";
const TEXT_STREAMING = "text_streaming";
const GENERAL_USE_BLUETOOTH = "general_use_bluetooth";
const GENERAL_TEST_DATA = "general_test_data";
const GENERAL_DOWNLOAD_AUDIO_FILES_BEFORE_PLAYING = "general_download_audio_files_before_playing";
const SPEECH_LANGUAGE = "speech_language";
const SPEECH_TEMPERATURE = "speech_temperature";
const TTS_STABILITY = "tts_stability";
const TTS_SIMILARITY = "tts_similarity";
const TTS_VOICE = "tts_voice";
const TTS_STREAMING = "tts_streaming";
const TTS_SPEED = "tts_speed";
const TTS_MODEL_NAME = "tts_model_name";
const TTS_AUTO_EXECUTE = "tts_auto_execute";
const IMAGE_MODEL_NAME = "image_model_name";
const IMAGE_NUMBER_IMAGES = "image_number_images";
const IMAGE_SIZE = "image_model_size";
const IMAGE_QUALITY_HD = "image_quality_id";
const IMAGE_DISABLE_SAFE_PROMPT = "image_disable_safe_prompt";
const IMAGE_AUTO_GENERATE_IMAGE = "image_auto_generate_image";
const IMAGE_ARTGEN_SHOW_PROMPT = "image_artgen_show_prompt";
const AUTH_TOKEN_FOR_BACKEND = "auth_token_for_backend";

// Default values
const defaultSettings = {
  [APP_MODE_PRODUCTION]: true,
  [APP_MODE_API_URL]: "https://ai.atamai.biz/api/",
  [APP_MODE_USE_WATSON]: false,
  [TEXT_MODEL_NAME]: "GPT-4o",
  [TEXT_TEMPERATURE]: 0.0,
  [TEXT_MEMORY_SIZE]: 2000,
  [TEXT_STREAMING]: false,
  [GENERAL_USE_BLUETOOTH]: false,
  [GENERAL_TEST_DATA]: false,
  [GENERAL_DOWNLOAD_AUDIO_FILES_BEFORE_PLAYING]: true,
  [SPEECH_LANGUAGE]: "en",
  [SPEECH_TEMPERATURE]: 0.0,
  [TTS_STABILITY]: 0.0,
  [TTS_SIMILARITY]: 0.0,
  [TTS_VOICE]: "alloy",
  [TTS_STREAMING]: false,
  [TTS_SPEED]: 1.0,
  [TTS_MODEL_NAME]: "tts-1",
  [TTS_AUTO_EXECUTE]: false,
  [IMAGE_MODEL_NAME]: "dall-e-3",
  [IMAGE_NUMBER_IMAGES]: 1,
  [IMAGE_SIZE]: 1024,
  [IMAGE_QUALITY_HD]: false,
  [IMAGE_DISABLE_SAFE_PROMPT]: false,
  [IMAGE_AUTO_GENERATE_IMAGE]: false,
  [IMAGE_ARTGEN_SHOW_PROMPT]: false,
  [AUTH_TOKEN_FOR_BACKEND]: "",
};

// Utility function to convert types
const convertType = (key, value) => {
  const typeMap = {
    [TEXT_TEMPERATURE]: 'float',
    [TEXT_MEMORY_SIZE]: 'int',
    [SPEECH_TEMPERATURE]: 'float',
    [TTS_STABILITY]: 'float',
    [TTS_SIMILARITY]: 'float',
    [TTS_SPEED]: 'float',
    [IMAGE_NUMBER_IMAGES]: 'int',
    [IMAGE_SIZE]: 'int',
  };

  const type = typeMap[key];
  switch (type) {
    case 'int':
      return parseInt(value, 10);
    case 'float':
      return parseFloat(value);
    case 'boolean':
      return value === 'true';
    default:
      return value;
  }
};

const getItem = (key, defaultValue) => {
  const value = localStorage.getItem(key);
  if (value !== null) {
    return convertType(key, JSON.parse(value));
  }
  return defaultValue;
};

const setItem = (key, value) => {
  localStorage.setItem(key, JSON.stringify(value));
};

// this needs to be only in memory - because we don't want to be preserved between web refreshes
let currentTextAICharacter = "assistant";

// Getter methods
export const getIsProdMode = () => getItem(APP_MODE_PRODUCTION, defaultSettings[APP_MODE_PRODUCTION]);
export const getAppModeApiUrl = () => getItem(APP_MODE_API_URL, defaultSettings[APP_MODE_API_URL]);
export const getAppModeUseWatson = () => getItem(APP_MODE_USE_WATSON, defaultSettings[APP_MODE_USE_WATSON]);
export const getDownloadAudioFilesBeforePlaying = () => getItem(GENERAL_DOWNLOAD_AUDIO_FILES_BEFORE_PLAYING, defaultSettings[GENERAL_DOWNLOAD_AUDIO_FILES_BEFORE_PLAYING]);
export const getTextModelName = () => getItem(TEXT_MODEL_NAME, defaultSettings[TEXT_MODEL_NAME]);
export const getTextAICharacter = () => { return currentTextAICharacter; };
export const getTextTemperature = () => getItem(TEXT_TEMPERATURE, defaultSettings[TEXT_TEMPERATURE]);
export const getTextMemorySize = () => getItem(TEXT_MEMORY_SIZE, defaultSettings[TEXT_MEMORY_SIZE]);
export const getIsStreamingEnabled = () => getItem(TEXT_STREAMING, defaultSettings[TEXT_STREAMING]);
export const getUseBluetooth = () => getItem(GENERAL_USE_BLUETOOTH, defaultSettings[GENERAL_USE_BLUETOOTH]);
export const getUseTestData = () => getItem(GENERAL_TEST_DATA, defaultSettings[GENERAL_TEST_DATA]);
export const getSpeechLanguage = () => getItem(SPEECH_LANGUAGE, defaultSettings[SPEECH_LANGUAGE]);
export const getSpeechTemperature = () => getItem(SPEECH_TEMPERATURE, defaultSettings[SPEECH_TEMPERATURE]);
export const getTTSStability = () => getItem(TTS_STABILITY, defaultSettings[TTS_STABILITY]);
export const getTTSSimilarity = () => getItem(TTS_SIMILARITY, defaultSettings[TTS_SIMILARITY]);
export const getTTSVoice = () => getItem(TTS_VOICE, defaultSettings[TTS_VOICE]);
export const getTTSStreaming = () => getItem(TTS_STREAMING, defaultSettings[TTS_STREAMING]);
export const getTTSSpeed = () => getItem(TTS_SPEED, defaultSettings[TTS_SPEED]);
export const getTTSModelName = () => getItem(TTS_MODEL_NAME, defaultSettings[TTS_MODEL_NAME]);
export const getTTSAutoExecute = () => getItem(TTS_AUTO_EXECUTE, defaultSettings[TTS_AUTO_EXECUTE]);
export const getImageModelName = () => getItem(IMAGE_MODEL_NAME, defaultSettings[IMAGE_MODEL_NAME]);
export const getImageNumberImages = () => getItem(IMAGE_NUMBER_IMAGES, defaultSettings[IMAGE_NUMBER_IMAGES]);
export const getImageSize = () => getItem(IMAGE_SIZE, defaultSettings[IMAGE_SIZE]);
export const getImageQualityHD = () => getItem(IMAGE_QUALITY_HD, defaultSettings[IMAGE_QUALITY_HD]);
export const getImageDisableSafePrompt = () => getItem(IMAGE_DISABLE_SAFE_PROMPT, defaultSettings[IMAGE_DISABLE_SAFE_PROMPT]);
export const getImageAutoGenerateImage = () => getItem(IMAGE_AUTO_GENERATE_IMAGE, defaultSettings[IMAGE_AUTO_GENERATE_IMAGE]);
export const getImageArtgenShowPrompt = () => getItem(IMAGE_ARTGEN_SHOW_PROMPT, defaultSettings[IMAGE_ARTGEN_SHOW_PROMPT]);
export const getAuthTokenForBackend = () => getItem(AUTH_TOKEN_FOR_BACKEND, defaultSettings[AUTH_TOKEN_FOR_BACKEND]);

// Setter methods
export const setIsProdMode = (value) => setItem(APP_MODE_PRODUCTION, value);
export const setAppModeApiUrl = (value) => setItem(APP_MODE_API_URL, value);
export const setAppModeUseWatson = (value) => setItem(APP_MODE_USE_WATSON, value);
export const setDownloadAudioFilesBeforePlaying = (value) => setItem(GENERAL_DOWNLOAD_AUDIO_FILES_BEFORE_PLAYING, value);
export const setTextModelName = (value) => setItem(TEXT_MODEL_NAME, value);
export const setTextAICharacter = (value) => { currentTextAICharacter = value; };
export const setTextTemperature = (value) => setItem(TEXT_TEMPERATURE, value);
export const setTextMemorySize = (value) => setItem(TEXT_MEMORY_SIZE, value);
export const setIsStreamingEnabled = (value) => setItem(TEXT_STREAMING, value);
export const setUseBluetooth = (value) => setItem(GENERAL_USE_BLUETOOTH, value);
export const setUseTestData = (value) => setItem(GENERAL_TEST_DATA, value);
export const setSpeechLanguage = (value) => setItem(SPEECH_LANGUAGE, value.toLowerCase());
export const setSpeechTemperature = (value) => setItem(SPEECH_TEMPERATURE, value);
export const setTTSStability = (value) => setItem(TTS_STABILITY, value);
export const setTTSSimilarity = (value) => setItem(TTS_SIMILARITY, value);
export const setTTSVoice = (value) => setItem(TTS_VOICE, value);
export const setTTSStreaming = (value) => setItem(TTS_STREAMING, value);
export const setTTSSpeed = (value) => setItem(TTS_SPEED, value);
export const setTTSModelName = (value) => setItem(TTS_MODEL_NAME, value);
export const setTTSAutoExecute = (value) => setItem(TTS_AUTO_EXECUTE, value);
export const setImageModelName = (value) => setItem(IMAGE_MODEL_NAME, value);
export const setImageNumberImages = (value) => setItem(IMAGE_NUMBER_IMAGES, value);
export const setImageSize = (value) => setItem(IMAGE_SIZE, value);
export const setImageQualityHD = (value) => setItem(IMAGE_QUALITY_HD, value);
export const setImageDisableSafePrompt = (value) => setItem(IMAGE_DISABLE_SAFE_PROMPT, value);
export const setImageAutoGenerateImage = (value) => setItem(IMAGE_AUTO_GENERATE_IMAGE, value);
export const setImageArtgenShowPrompt = (value) => setItem(IMAGE_ARTGEN_SHOW_PROMPT, value);
export const setAuthTokenForBackend = (value) => setItem(AUTH_TOKEN_FOR_BACKEND, value);

// Depending if it's production mode and also depending on which internal API server is in use
export const setURLForAPICalls = () => {
  const url = getIsProdMode()
    ? "https://ai.atamai.biz/api"
    : getAppModeUseWatson()
      ? "http://192.168.1.123:8000"
      //: "http://192.168.1.150:8000";
      : "http://localhost:8000";
  setAppModeApiUrl(url);
};

// Used for API calls - to prepare dict with all settings
export const getSettingsDict = () => ({
  text: {
    temperature: getTextTemperature(),
    model: getTextModelName(),
    memory_limit: getTextMemorySize(),
    ai_character: getTextAICharacter(),
    streaming: getIsStreamingEnabled(),
  },
  tts: {
    stability: getTTSStability(),
    similarity_boost: getTTSSimilarity(),
    voice: getTTSVoice(),
    streaming: getTTSStreaming(),
    speed: getTTSSpeed(),
    model: getTTSModelName(),
  },
  speech: {
    language: getSpeechLanguage(),
    temperature: getSpeechTemperature(),
  },
  image: {
    model: getImageModelName(),
    number_of_images: getImageNumberImages(),
    size_of_image: getImageSize(),
    quality_hd: getImageQualityHD(),
    disable_safe_prompt_adjust: getImageDisableSafePrompt(),
  },
  general: {
    returnTestData: getUseTestData(),
  },
});
