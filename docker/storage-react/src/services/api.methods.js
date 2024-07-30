// api.methods.js
import makeApiCall from './api.service';
import { getSettingsDict } from '../utils/configuration';
import { formatDate } from '../utils/misc';
import config from "../config";

// helper function to prepare data for DB request in proper format - as it is used in few places
const prepareChatHistoryForDB = (chatContent) => {
  // prepare chat history for DB in expected format (same as android)
  const chatHistoryForDB = (chatContent.messages || []).map((message) => ({
    "message": message.message,
    "isUserMessage": message.isUserMessage,
    "imageLocations": message.imageLocations || [],
    "fileNames": message.fileNames || [],
    "aiCharacterName": message.aiCharacterName || "",
    "messageId": message.messageId || 0,
    "apiAIModelName": message.apiAIModelName,
    "dateGenerate": message.dateGenerate ? formatDate(message.dateGenerate) : null,
    "isTTS": message.isTTS || false,
    "showTranscribeButton": message.showTranscribeButton || false,
    "isGPSLocationMessage": message.isGPSLocationMessage || false
  }));
  return chatHistoryForDB;
}

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

const triggerStreamingAPIRequest = async (endpoint, category, action, userInput, assetInput, { onChunkReceived, onStreamEnd, onError }) => {
  const API_BASE_URL = `${config.apiEndpoint}/${endpoint}`;

  const apiBody = {
    category: category,
    action: action,
    userInput: userInput,
    assetInput: assetInput,
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

const generateImage = async (image_prompt) => {
  try {
    const userInput = { "text": image_prompt };
    const response = await triggerAPIRequest("generate", "image", "generate", userInput);
    if (response.success) {
      return response.message.result;
    } else {
      throw new Error('Failed to generate image');
    }
  } catch (error) {
    console.error('Error generating image:', error);
    throw error;
  }
}

const updateSessionInDB = async (chatContent, sessionId) => {
  //db_update_session to DB 
  const chatHistoryForDB = prepareChatHistoryForDB(chatContent);
  const finalInputForDB = {
    "session_id": sessionId,
    "chat_history": chatHistoryForDB
  }
  await apiMethods.triggerAPIRequest("api/db", "provider.db", "db_update_session", finalInputForDB);
}

const apiMethods = {
  triggerAPIRequest, triggerStreamingAPIRequest, uploadFileToS3, prepareChatHistoryForDB, generateImage, updateSessionInDB
};

export default apiMethods;

