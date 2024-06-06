const config = {
  // userSettings here are temporarily - in auth.service i later manage it 
  // and use the function getUserSettings() to get the settings
  // eventually move it to DB
  userSettings: {
    "text": {
      "generator": "openai",
      "temperature": 0.2,
      "model": "gpt-3.5-turbo",
      //"model": "gpt-4",
      "memory_limit": 1000,
      "textGenStreaming": true,
      //"textGenStreaming": false,
    },
    "image": {
      "generator": "sd",
      //"generator": "openai",
      //"generator": "mj",
      "number_of_images": 1,
      "size_of_image": 512,
      "sd_engine_id": "stable-diffusion-xl-beta-v2-2-2",
      //"sd_engine_id": "stable-diffusion-512-v2-1",
      //"sd_engine_id": "stable-diffusion-768-v2-1",
      //"sd_number_of_steps": 50,
      //"sd_cfg_scale": 11,
    },
    "audio": {
      "generator": "elevenlabs",
      "voice": "Sherlock",
      "stability": 0.8,
      "similarity_boost": 0.95,
    },
    "speech": {
      "generator": "openai",
      "temperature": 0.1,
      "response_format": "text",
      "language": "en"
    },
    "replicate": {
      "generator": "replicate",
    },
    "plant": {
      "generator": "plant_id",
    },
    "general": {
      "useServiceWorkers": false,
      "returnTestData": false,
      //"returnTestData": true,
    },
  },
};

if (process.env.NODE_ENV === 'production') {
    config.AWS_REGION = 'eu-west-1';
    config.S3_BUCKET = "mn-contentautomation";
    config.apiNodeEndpoint = "https://www.kamba.me/api";
    config.apiFastEndpoint = "https://www.kamba.me/fast";
    config.userSettings.imageGenerator = "sd";
    config.userSettings.general.returnTestData = false;
} else if  (process.env.NODE_ENV === 'development') {
    config.AWS_REGION = 'eu-west-1';
    config.S3_BUCKET = "mn-contentautomation-nonprod";
    config.apiNodeEndpoint = "https://test.kamba.me/api";
    config.apiFastEndpoint = "https://test.kamba.me/fast";
    //config.apiNodeEndpoint = "http://192.168.1.250:3020/api";
    //config.apiFastEndpoint = "http://192.168.1.250:8000";

    if (process.env.REACT_APP_MY_NODE_ENV === 'local') {
      config.AWS_REGION = 'eu-west-1';
      config.S3_BUCKET = "mn-contentautomation-nonprod";
      //config.apiNodeEndpoint = "http://192.168.50.160:3020/api";
      //config.apiFastEndpoint = "http://localhost:8000";
      config.apiNodeEndpoint = "https://test.kamba.me/api";
      config.apiFastEndpoint = "https://test.kamba.me/fast";
    }
}

config.DEBUG = 1;
config.VERBOSE_SUPERB = 0;
export default config;
