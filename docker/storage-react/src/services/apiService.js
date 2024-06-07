// apiService.js
import makeApiCall from './api.service';

const API_BASE_URL = 'http://192.168.1.101:8000/api/db';

const fetchChatSessions = async () => {
    try {
        const apiBody = {
            category: 'provider.db',
            action: 'db_all_sessions_for_user',
            userInput: { limit: 10, offset: 0 },
            userSettings: {},
            customerId: 1,
        }
        const response = await makeApiCall({
            endpoint: API_BASE_URL,
            method: "POST",
            body: apiBody
        });

        console.log('API response:', response);
        console.log('API response:', response.message);
        console.log('API response:', response.message.result);
        return response.message.result;
    } catch (error) {
        console.error('Error fetching chat sessions:', error);
        throw error;
    }

}

const fetchChatContent = async (sessionId) => {
  try {
    const apiBody = {
      category: 'provider.db',
      action: 'db_get_user_session',
      userInput: { "session_id": sessionId },
      userSettings: {},
      customerId: 1,
    }
    const response = await makeApiCall({
        endpoint: API_BASE_URL,
        method: "POST",
        body: apiBody
    });

    console.log('API response:', response);
    console.log('API response:', response.message);
    console.log('API response:', response.message.result);
    return response.message;

  } catch (error) {
    console.error('Error fetching chat content:', error);
    throw error;
  }
};

const authUser = async (user, password) => {
  try {
    const apiBody = {
      category: 'provider.db',
      action: 'db_auth_user',
      userInput: { "username": user, "password": password },
      userSettings: {},
      customerId: 1,
    }
    const response = await makeApiCall({
        endpoint: API_BASE_URL,
        method: "POST",
        body: apiBody
    });

    console.log('API response:', response);
    console.log('API response:', response.message);
    console.log('API response:', response.message.result);
    return response.message;

  } catch (error) {
    console.error('Error fetching chat content:', error);
    throw error;
  }
};

/*
const fetchChatSessionsOLD = async () => {
  try {
    const response = await axios.post(API_BASE_URL, {
      category: 'provider.db',
      action: 'db_all_sessions_for_user',
      userInput: { limit: 10, offset: 0 },
      userSettings: {},
      customerId: 1,
    });
    console.log('API response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching chat sessions:', error);
    throw error;
  }
};

const fetchChatContent = async (sessionId) => {
  try {
    const response = await axios.post(API_BASE_URL, {
      category: 'provider.db',
      action: 'db_get_session_content',
      userInput: { sessionId },
      userSettings: {},
      customerId: 1,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching chat content:', error);
    throw error;
  }
};
*/
export default {
  fetchChatSessions,
  fetchChatContent,
  authUser
};
