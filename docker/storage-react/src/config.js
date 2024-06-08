const config = {
  // userSettings here are temporarily - in auth.service i later manage it 
  // and use the function getUserSettings() to get the settings
  // eventually move it to DB
  userSettings: {
    "text": {
      "temperature": 0.2,
      "model": "gpt-3.5-turbo",
      "memory_limit": 1000,
      "streaming": true,
    },
    "image": {
      "model": "dall-e-3",
      "number_of_images": 1,
      "size_of_image": 1024,
      "quality_hd": false,
      "disable_safe_prompt_adjust": false,
    },
    "tts": {
      "voice": "Sherlock",
      "stability": 0.8,
      "similarity_boost": 0.95,
      "streaming": true,
      "speed": 1,
      "model": "tts",
    },
    "speech": {
      "temperature": 0.1,
      "language": "en"
    },
    "general": {
      "returnTestData": false,
      //"returnTestData": true,
    },
  },
};

if (process.env.NODE_ENV === 'production') {
    config.AWS_REGION = 'eu-west-1';
    config.S3_BUCKET = "myaiapps3bucket";
    config.apiEndpoint = "https://ai.atamai.biz/api";
} else if  (process.env.NODE_ENV === 'development') {
    config.AWS_REGION = 'eu-west-1';
    config.S3_BUCKET = "myaiapps3bucket";
    config.apiEndpoint = "http://192.168.1.101:8000/api"

    if (process.env.REACT_APP_MY_NODE_ENV === 'local') {
      config.AWS_REGION = 'eu-west-1';
      config.S3_BUCKET = "myaiapps3bucket";
      config.apiEndpoint = "http://localhost:8000/api";
    }
}

config.MY_AUTH_TOKEN = process.env.MY_AUTH_TOKEN;
config.DEBUG = 1;
config.VERBOSE_SUPERB = 0;
export default config;
