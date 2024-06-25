// api.methods.js
import makeApiCall from './api.service';
import { getSettingsDict } from '../utils/configuration';
import config from "../config";

const triggerAPIRequest = async (endpoint, category, action, userInput) => {
  const API_BASE_URL = `${config.apiEndpoint}/${endpoint}`;

  try {
    const apiBody = {
      category: category,
      action: action,
      userInput: userInput,
      userSettings: getSettingsDict(),
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

const triggerStreamingAPIRequest = async (endpoint, category, action, userInput, { onChunkReceived, onStreamEnd, onError }) => {
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
      onChunkReceived: onChunkReceived,
      onStreamEnd: onStreamEnd
    });
  } catch (error) {
    onError(error);
    console.error('Error during streaming:', error);
  }
}

const uploadFileToS3 = async (endpoint, category, action, file) => {
  const API_BASE_URL = `${config.apiEndpoint}/${endpoint}`;

  const formData = new FormData();
  formData.append('file', file);
  formData.append('category', category);
  formData.append('action', action);
  formData.append('userInput', JSON.stringify({}));
  formData.append('userSettings', JSON.stringify(getSettingsDict()));
  formData.append('customerId', 1);

  const response = await makeApiCall({
    endpoint: API_BASE_URL,
    method: 'POST',
    body: formData,
    headers: {}, // Ensure headers are set correctly for FormData
  });

  return response;
};


const apiMethods = {
  triggerAPIRequest, triggerStreamingAPIRequest, uploadFileToS3
};

export default apiMethods;

