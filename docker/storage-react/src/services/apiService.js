// apiService.js
import makeApiCall from './api.service';
import config from "../config";

const triggerDBRequest = async (endpoint, action, userInput) => {
  const API_BASE_URL = `${config.apiEndpoint}/${endpoint}`;

  try {
      const apiBody = {
          category: 'provider.db',
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

      console.log('API response:', response);
      return response;
  } catch (error) {
      console.error('Error triggering DB request:', error);
      throw error;
  }
}

const apiService = {
  triggerDBRequest,
};

export default apiService;

