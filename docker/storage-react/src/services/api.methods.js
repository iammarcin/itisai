// api.methods.js
import makeApiCall from './api.service';
import { getSettingsDict } from '../utils/local.storage';
import config from "../config";

const triggerAPIRequest = async (endpoint, category, action, userInput) => {
  const API_BASE_URL = `${config.apiEndpoint}/${endpoint}`;

  try {
    const apiBody = {
      category: category,
      action: action,
      userInput: userInput,
      userSettings: {},
      customerId: 1,
    }
    const response = await makeApiCall({
      endpoint: API_BASE_URL,
      method: "POST",
      body: apiBody
    });

    return response;
  } catch (error) {
    console.error('Error triggering DB request:', error);
    throw error;
  }
}

const triggerStreamingAPIRequest = async (endpoint, category, action, userInput) => {
  const API_BASE_URL = `${config.apiEndpoint}/${endpoint}`;

  const apiBody = {
    category: category,
    action: action,
    userInput: userInput,
    userSettings: getSettingsDict(),
    customerId: 1,
  };

  try {
    await makeApiCall({
      endpoint: API_BASE_URL,
      method: 'POST',
      body: apiBody,
      streamResponse: true,
      onChunkReceived: (chunk) => {
        console.log("Chunk received:", chunk);
      },
      onStreamEnd: () => {
        console.log("Stream ended");
      }
    });
  } catch (error) {
    console.error('Error during streaming:', error);
  }
}

const apiMethods = {
  triggerAPIRequest, triggerStreamingAPIRequest
};

export default apiMethods;

