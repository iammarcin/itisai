// ChatHandleAPI.js
import config from '../config';
import apiMethods from '../services/api.methods';
import { getTextAICharacter, getImageArtgenShowPrompt, getImageAutoGenerateImage } from '../utils/configuration';

// to clarify some of params:
// sessionIndexForAPI, sessionIdForAPI - those are needed because we want to be sure that we're generating data for proper session (if user switches or whatever happens)
// setCurrentSessionId - those are needed because we need to set global session (for example when we save in DB and new session is generated)
const ChatHandleAPI = async ({
  userInput, attachedImages, sessionIndexForAPI, sessionIdForAPI, setCurrentSessionId, chatContent, setChatContent, setIsLoading, setErrorMsg, manageProgressText
}) => {
  setIsLoading(true);
  manageProgressText("show", "Text");

  console.log("Current chatContent: ", chatContent);

  // Add the user message to chat content
  const userMessage = { message: userInput, isUserMessage: true, imageLocations: attachedImages.map(image => image.url) };
  const updatedChatContent = [...chatContent];
  updatedChatContent[sessionIndexForAPI].ai_character_name = getTextAICharacter()
  updatedChatContent[sessionIndexForAPI].messages.push(userMessage);
  setChatContent(updatedChatContent);

  // prepare user input for API call
  const finalUserInput = {
    "prompt": [
      { "type": "text", "text": userInput },
      ...attachedImages.map(image => ({ "type": "image_url", "image_url": { "url": image.url } }))
    ],
    "chat_history": (chatContent[sessionIndexForAPI].messages || []).map((message) => ({
      "role": message.isUserMessage ? "user" : "assistant",
      "content": [
        { "type": "text", "text": message.message },
        ...(message.imageLocations || []).map(imageUrl => ({ "type": "image_url", "image_url": { "url": imageUrl } }))
      ]
    }))
  };

  // Buffer to hold the chunks until the message is complete
  let chunkBuffer = '';
  let aiMessageIndex;

  // Add a placeholder for the AI message
  const aiMessagePlaceholder = {
    message: '',
    isUserMessage: false,
    imageLocations: [],
    aiCharacterName: getTextAICharacter()
  };

  updatedChatContent[sessionIndexForAPI].messages.push(aiMessagePlaceholder);
  aiMessageIndex = updatedChatContent[sessionIndexForAPI].messages.length - 1;
  setChatContent(updatedChatContent);

  try {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("API call. Final User Input", finalUserInput);
    }
    await apiMethods.triggerStreamingAPIRequest("chat", "text", "chat", finalUserInput, {
      onChunkReceived: (chunk) => {
        // if it's artgen and user disabled show prompt - don't show it
        if (getTextAICharacter() === "tools_artgen" && getImageArtgenShowPrompt() === false) {
          return
        }
        chunkBuffer += chunk;
        console.log("Text / Image chunk and sessionIndexForAPI: ", chunk, sessionIndexForAPI);
        updatedChatContent[sessionIndexForAPI].messages[aiMessageIndex].message = chunkBuffer;
        setChatContent([...updatedChatContent]);
      },
      onStreamEnd: async (fullResponse) => {
        manageProgressText("hide", "Text")
        console.log("fullResponse: ", fullResponse);

        // for artgen mode - if image is enabled and no images attached - generate image
        if (getTextAICharacter() === "tools_artgen" && getImageAutoGenerateImage() && attachedImages.length === 0) {
          manageProgressText("show", "Image")
          const userInput = { "text": fullResponse };
          await apiMethods.triggerAPIRequest("generate", "image", "generate", userInput).then((response) => {
            if (response.success) {
              console.log("Image sessionIndexForAPI: ", sessionIndexForAPI);
              setChatContent((prevChatContent) => {
                // Make sure we update the correct session
                const updatedContent = [...prevChatContent];
                console.log("inside image update prevChatContent", prevChatContent)
                updatedContent[sessionIndexForAPI].messages[aiMessageIndex].imageLocations = [response.message.result];
                console.log("inside image update updatedContent", updatedContent)
                return updatedContent;
              });
              //updatedChatContent[sessionIndexForAPI].messages[aiMessageIndex].imageLocations = [response.message.result];
              //setChatContent([...updatedChatContent]);
              manageProgressText("hide", "Image");
            } else {
              setErrorMsg("Problem generating image");
              manageProgressText("hide", "Image");
            }
          });
        }

        // save to DB
        // get user chatContent 
        var currentUserMessage = chatContent[sessionIndexForAPI].messages[chatContent[sessionIndexForAPI].messages.length - 2]
        var currentAIResponse = chatContent[sessionIndexForAPI].messages[chatContent[sessionIndexForAPI].messages.length - 1]

        console.log("chatContent", chatContent)

        // prepare chat history for DB in expected format (same as android)
        const chatHistoryForDB = (chatContent[sessionIndexForAPI].messages || []).map((message) => ({
          "message": message.message,
          "isUserMessage": message.isUserMessage,
          "imageLocations": message.imageLocations || [],
          "fileNames": message.fileNames || [],
          "aiCharacterName": message.aiCharacterName || "",
          "messageId": message.messageId || 0,
          "isTTS": message.isTTS || false,
          "showTranscribeButton": message.showTranscribeButton || false,
          "isGPSLocationMessage": message.isGPSLocationMessage || false
        }));

        const finalInputForDB = {
          "customer_id": 1,
          "session_id": sessionIdForAPI,
          "userMessage": {
            "sender": "User",
            "message": currentUserMessage.message,
            "message_id": currentUserMessage.message_id || 0,
            "image_locations": currentUserMessage.imageLocations || [],
            "file_locations": currentUserMessage.fileNames || [],
          },
          "aiResponse": {
            "sender": "AI",
            "message": currentAIResponse.message,
            "message_id": currentAIResponse.message_id || 0,
            "image_locations": currentAIResponse.imageLocations || [],
            "file_locations": currentAIResponse.fileNames || [],
          },
          "chat_history": chatHistoryForDB
        }

        await apiMethods.triggerAPIRequest("api/db", "provider.db", "db_new_message", finalInputForDB).then((response) => {
          if (response.success) {
            // update session in chatContent (will be useful later when switching session in top menu) and set current session id
            updatedChatContent[sessionIndexForAPI].sessionId = response.message.result.sessionId;
            setCurrentSessionId(response.message.result.sessionId);
            // update messageId in chatContent
            currentAIResponse.messageId = response.message.result.aiMessageId;
            currentUserMessage.messageId = response.message.result.userMessageId;

          } else {
            setErrorMsg("Problem saving in DB");
          }
        });

        setIsLoading(false);
        manageProgressText("hide", "Text")
      },
      onError: (error) => {
        setIsLoading(false);
        manageProgressText("hide", "Text")
        setErrorMsg("Error during streaming. Try again.")
        console.error('Error during streaming:', error);
      }
    });
  } catch (error) {
    setIsLoading(false);
    manageProgressText("hide", "Text")
    setErrorMsg("Error during streaming. Try again.")
    console.error('Error during streaming:', error);
  }
}

export default ChatHandleAPI;
