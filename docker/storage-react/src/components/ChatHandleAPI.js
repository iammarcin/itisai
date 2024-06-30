// ChatHandleAPI.js
import config from '../config';
import apiMethods from '../services/api.methods';
import { getTextAICharacter, getImageArtgenShowPrompt, getImageAutoGenerateImage } from '../utils/configuration';
import { characters } from './ChatCharacters';

// to clarify some of params:
// sessionIndexForAPI, sessionIdForAPI - those are needed because we want to be sure that we're generating data for proper session (if user switches or whatever happens)
// setCurrentSessionId - those are needed because we need to set global session (for example when we save in DB and new session is generated)
const ChatHandleAPI = async ({
  userInput, attachedImages, sessionIndexForAPI, sessionIdForAPI, setCurrentSessionId, chatContent, setChatContent, setFocusInput, setRefreshChatSessions, setIsLoading, setErrorMsg, manageProgressText, scrollToBottom
}) => {
  setIsLoading(true);
  manageProgressText("show", "Text");

  // Add the user message to chat content
  const userMessage = { message: userInput, isUserMessage: true, imageLocations: attachedImages.map(image => image.url) };
  const updatedChatContent = [...chatContent];
  updatedChatContent[sessionIndexForAPI].ai_character_name = getTextAICharacter()
  updatedChatContent[sessionIndexForAPI].messages.push(userMessage);
  setChatContent(updatedChatContent);

  // get current character (later we will check if auto response is set)
  const currentCharacter = characters.find(character => character.nameForAPI === getTextAICharacter());

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
    if (currentCharacter.autoResponse) {
      await apiMethods.triggerStreamingAPIRequest("chat", "text", "chat", finalUserInput, {
        onChunkReceived: (chunk) => {
          // if it's artgen and user disabled show prompt - don't show it
          if (getTextAICharacter() === "tools_artgen" && getImageArtgenShowPrompt() === false) {
            return
          }
          chunkBuffer += chunk;
          updatedChatContent[sessionIndexForAPI].messages[aiMessageIndex].message = chunkBuffer;
          setChatContent([...updatedChatContent]);
          scrollToBottom(sessionIndexForAPI);
        },
        onStreamEnd: async (fullResponse) => {
          manageProgressText("hide", "Text");
          scrollToBottom(sessionIndexForAPI);

          // save to DB
          // get user chatContent 
          var currentUserMessage = chatContent[sessionIndexForAPI].messages[chatContent[sessionIndexForAPI].messages.length - 2]
          var currentAIResponse = chatContent[sessionIndexForAPI].messages[chatContent[sessionIndexForAPI].messages.length - 1]

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
            "chat_history": apiMethods.prepareChatHistoryForDB(chatContent[sessionIndexForAPI])
          }

          await apiMethods.triggerAPIRequest("api/db", "provider.db", "db_new_message", finalInputForDB).then((response) => {
            if (response.success) {
              // update session in chatContent (will be useful later when switching session in top menu) and set current session id
              updatedChatContent[sessionIndexForAPI].sessionId = response.message.result.sessionId;
              setCurrentSessionId(response.message.result.sessionId);
              if (!sessionIdForAPI) {
                // this is needed - because for example image generation is triggered later then this step - so if sessionIdForAPI is not set - it fails to update in DB
                sessionIdForAPI = response.message.result.sessionId;
              }
              // update messageId in chatContent
              currentAIResponse.messageId = response.message.result.aiMessageId;
              currentUserMessage.messageId = response.message.result.userMessageId;
            }
          });

          // for artgen mode - if image is enabled and no images attached - generate image
          if (getTextAICharacter() === "tools_artgen" && getImageAutoGenerateImage() && attachedImages.length === 0) {
            manageProgressText("show", "Image");
            try {
              const imageLocation = await apiMethods.generateImage(fullResponse);
              if (imageLocation) {
                // update chatContent with generated image
                /*setChatContent((prevChatContent) => {
                  // Make sure we update the correct session
                  const updatedContent = [...prevChatContent];
                  updatedContent[sessionIndexForAPI].messages[aiMessageIndex].imageLocations = [response.message.result];
                  return updatedContent;
                });*/
                updatedChatContent[sessionIndexForAPI].messages[aiMessageIndex].imageLocations = [imageLocation];
                console.log("updatedChatContent", updatedChatContent)
                setChatContent([...updatedChatContent]);

                manageProgressText("hide", "Image");
                scrollToBottom(sessionIndexForAPI);
                setFocusInput(true);
                //db_update_session to DB 
                await apiMethods.updateSessionInDB(chatContent[sessionIndexForAPI], sessionIdForAPI);
              } else {
                setErrorMsg("Problem generating image");
                manageProgressText("hide", "Image");
              }
            } catch (error) {
              setIsLoading(false);
              manageProgressText("hide", "Text")
              setErrorMsg("Error during streaming. Try again.")
              console.error('Error during streaming:', error);
              console.error(error);
            } finally {
              manageProgressText("hide", "Image");
            }
          }
        }
      });
    } else {
      // Only send the user message to DB if autoResponse is false
      const finalInputForDB = {
        "customer_id": 1,
        "session_id": sessionIdForAPI,
        "userMessage": {
          "sender": "User",
          "message": userInput,
          "message_id": 0,
          "image_locations": attachedImages.map(image => image.url),
          "file_locations": [],
        },
        "chat_history": apiMethods.prepareChatHistoryForDB(chatContent[sessionIndexForAPI])
      };

      await apiMethods.triggerAPIRequest("api/db", "provider.db", "db_new_message", finalInputForDB).then((response) => {
        if (response.success) {
          updatedChatContent[sessionIndexForAPI].sessionId = response.message.result.sessionId;
          setCurrentSessionId(response.message.result.sessionId);
        }
      }).catch((error) => {
        setIsLoading(false);
        manageProgressText("hide", "Text");
        setErrorMsg("Error saving message. Try again.");
        console.error('Error saving message:', error);
      });
    }

    setIsLoading(false);
    manageProgressText("hide", "Text");
    setFocusInput(true);

    // refresh sidebar chat sessions (only once - when we have initial messages - not to keep refreshing all the time)
    if ((currentCharacter.autoResponse && chatContent[sessionIndexForAPI].messages.length < 3) ||
      (!currentCharacter.autoResponse && chatContent[sessionIndexForAPI].messages.length < 2)) {
      setRefreshChatSessions(true);
    }


  } catch (error) {
    setIsLoading(false);
    manageProgressText("hide", "Text")
    setErrorMsg("Error during streaming. Try again.")
    console.error('Error during streaming:', error);
  }
}

export default ChatHandleAPI;
