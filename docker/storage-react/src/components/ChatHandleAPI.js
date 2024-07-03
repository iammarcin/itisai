// ChatHandleAPI.js
import config from '../config';
import apiMethods from '../services/api.methods';
import { getTextAICharacter, setTextAICharacter, getOriginalAICharacter, setOriginalAICharacter, getImageArtgenShowPrompt, getImageAutoGenerateImage } from '../utils/configuration';
import { characters } from './ChatCharacters';

// to clarify some of params:
// editMessagePosition - this is set to index of edited message - if its null its normal, new message, if not - it is edited message
// sessionIndexForAPI, sessionIdForAPI - those are needed because we want to be sure that we're generating data for proper session (if user switches or whatever happens)
// setCurrentSessionId - those are needed because we need to set global session (for example when we save in DB and new session is generated)
// currentSessionIndex - also needed - as we're checking if currently generating in active session
const ChatHandleAPI = async ({
  userInput, editMessagePosition, attachedImages, currentSessionIndex, sessionIndexForAPI, sessionIdForAPI, setCurrentSessionId, chatContent, setChatContent, setFocusInput, setRefreshChatSessions, setIsLoading, setErrorMsg, manageProgressText, scrollToBottom
}) => {
  setIsLoading(true);
  manageProgressText("show", "Text");

  // Add the user message to chat content
  const userMessage = { message: userInput, isUserMessage: true, imageLocations: attachedImages.map(image => image.url) };
  const updatedChatContent = [...chatContent];
  if (!updatedChatContent[sessionIndexForAPI].ai_character_name)
    updatedChatContent[sessionIndexForAPI].ai_character_name = getTextAICharacter()

  // get current character (later we will check if auto response is set)
  const currentCharacter = characters.find(character => character.nameForAPI === getTextAICharacter());

  // collect chat history (needed to send it API to get whole context of chat)
  // (excluding the latest message - as this will be sent via userPrompt), including images if any
  // or excluding 2 last messages - if its edited user message
  var chatHistory = chatContent[sessionIndexForAPI].messages;

  if (editMessagePosition !== null) {
    chatHistory = chatHistory.slice(0, -2);
  }

  const finalUserInput = {
    "prompt": [
      { "type": "text", "text": userInput },
      ...attachedImages.map(image => ({ "type": "image_url", "image_url": { "url": image.url } }))
    ],
    "chat_history": (chatHistory.map((message) => ({
      "role": message.isUserMessage ? "user" : "assistant",
      "content": [
        { "type": "text", "text": message.message },
        ...(message.imageLocations || []).map(imageUrl => ({ "type": "image_url", "image_url": { "url": imageUrl } }))
      ]
    }))),
  };

  // Add or replace user message
  if (editMessagePosition === null) {
    updatedChatContent[sessionIndexForAPI].messages.push(userMessage);
  } else {
    updatedChatContent[sessionIndexForAPI].messages[editMessagePosition.index].message = userInput;
    updatedChatContent[sessionIndexForAPI].messages[editMessagePosition.index].imageLocations = attachedImages.map(image => image.url);
  }
  setChatContent(updatedChatContent);

  // Buffer to hold the chunks until the message is complete
  let chunkBuffer = '';
  let aiMessageIndex;

  try {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("API call. Final User Input", finalUserInput);
    }
    if (currentCharacter.autoResponse) {
      if (editMessagePosition === null) {
        // Add a placeholder for the AI message
        const aiMessagePlaceholder = {
          message: '',
          isUserMessage: false,
          imageLocations: [],
          aiCharacterName: getTextAICharacter()
        };
        updatedChatContent[sessionIndexForAPI].messages.push(aiMessagePlaceholder);
        aiMessageIndex = updatedChatContent[sessionIndexForAPI].messages.length - 1;
      } else {
        // if its edited message - overwrite AI response
        aiMessageIndex = editMessagePosition.index + 1;
        // but if it doesn't exist - let's create it
        if (aiMessageIndex >= updatedChatContent[sessionIndexForAPI].messages.length) {
          const aiMessagePlaceholder = {
            message: '',
            isUserMessage: false,
            imageLocations: [],
            aiCharacterName: getTextAICharacter()
          };
          updatedChatContent[sessionIndexForAPI].messages.push(aiMessagePlaceholder);
        } else {
          // if exists - overwrite
          updatedChatContent[sessionIndexForAPI].messages[aiMessageIndex].message = '';
        }
      }

      setChatContent(updatedChatContent);

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
          const currentUserMessage = updatedChatContent[sessionIndexForAPI].messages[aiMessageIndex - 1];
          const currentAIResponse = updatedChatContent[sessionIndexForAPI].messages[aiMessageIndex];

          const finalInputForDB = {
            "customer_id": 1,
            "session_id": sessionIdForAPI,
            "userMessage": {
              "sender": "User",
              "message": currentUserMessage.message,
              "message_id": currentUserMessage.messageId || 0,
              "image_locations": currentUserMessage.imageLocations || [],
              "file_locations": currentUserMessage.fileNames || [],
            },
            "aiResponse": {
              "sender": "AI",
              "message": currentAIResponse.message,
              "message_id": currentAIResponse.messageId || 0,
              "image_locations": currentAIResponse.imageLocations || [],
              "file_locations": currentAIResponse.fileNames || [],
            },
            "chat_history": apiMethods.prepareChatHistoryForDB(chatContent[sessionIndexForAPI])
          }

          var apiCallDbMethod = "db_new_message";
          if (editMessagePosition !== null) {
            apiCallDbMethod = "db_edit_message";
          }
          await apiMethods.triggerAPIRequest("api/db", "provider.db", apiCallDbMethod, finalInputForDB).then((response) => {
            if (response.success) {
              // update session in chatContent (will be useful later when switching session in top menu) and set current session id
              if (!updatedChatContent[sessionIndexForAPI].sessionId) {
                updatedChatContent[sessionIndexForAPI].sessionId = response.message.result.sessionId;
                setCurrentSessionId(response.message.result.sessionId);
              }
              if (!sessionIdForAPI) {
                // this is needed - because for example image generation is triggered later then this step - so if sessionIdForAPI is not set - it fails to update in DB
                sessionIdForAPI = response.message.result.sessionId;
              }
              // update messageId in chatContent
              if (response.message.result.aiMessageId)
                currentAIResponse.messageId = response.message.result.aiMessageId;
              if (response.message.result.userMessageId)
                currentUserMessage.messageId = response.message.result.userMessageId;
            }
          });

          console.log("current AI char: ", getTextAICharacter())
          console.log("currentAIResponse.aiCharacterName", currentAIResponse.aiCharacterName)
          // for artgen mode - if image is enabled and no images attached - generate image
          if (currentAIResponse.aiCharacterName === "tools_artgen" && getImageAutoGenerateImage() && attachedImages.length === 0) {
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
          "message_id": editMessagePosition !== null ? editMessagePosition.messageId : 0,
          "image_locations": attachedImages.map(image => image.url),
          "file_locations": [],
        },
        "chat_history": apiMethods.prepareChatHistoryForDB(chatContent[sessionIndexForAPI])
      };

      var apiCallDbMethod = "db_new_message";
      if (editMessagePosition !== null) {
        apiCallDbMethod = "db_edit_message";
      }
      await apiMethods.triggerAPIRequest("api/db", "provider.db", apiCallDbMethod, finalInputForDB).then((response) => {
        if (response.success) {
          // update sessionID (from DB) for this chat session
          if (!updatedChatContent[sessionIndexForAPI].sessionId)
            updatedChatContent[sessionIndexForAPI].sessionId = response.message.result.sessionId;
          // update current message with userMessageId
          updatedChatContent[sessionIndexForAPI].messages[updatedChatContent[sessionIndexForAPI].messages.length - 1].messageId = response.message.result.userMessageId;
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

    // only if it's current session
    if (sessionIndexForAPI === currentSessionIndex) {
      // fallback to original AI character (after single use of different one)
      if (getOriginalAICharacter()) {
        setTextAICharacter(getOriginalAICharacter());
        setOriginalAICharacter(null);
      }
    }

  } catch (error) {
    setIsLoading(false);
    manageProgressText("hide", "Text")
    setErrorMsg("Error during streaming. Try again.")
    console.error('Error during streaming:', error);
  }
}

export default ChatHandleAPI;
