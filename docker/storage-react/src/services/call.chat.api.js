// services/call.chat.api.js

import config from '../config';
import apiMethods from './api.methods';
import { setTextAICharacter, getOriginalAICharacter, setOriginalAICharacter, getImageArtgenShowPrompt, getImageAutoGenerateImage } from '../utils/configuration';
import { characters } from '../components/ChatCharacters';
import { formatDate } from '../utils/misc';

// to clarify some of params:
// editMessagePosition - this is set to index of edited message - if its null its normal, new message, if not - it is edited message
// sessionIndexForAPI, sessionIdForAPI - those are needed because we want to be sure that we're generating data for proper session (if user switches or whatever happens)
// setCurrentSessionId - those are needed because we need to set global session (for example when we save in DB and new session is generated)
// currentSessionIndex - also needed - as we're checking if currently generating in active session
// apiAIModelName - model name that we are using for generating the message (sent to API). this will be recorded in order to show which model generated each message
const CallChatAPI = async ({
  userInput, editMessagePosition, attachedImages, attachedFiles, currentSessionIndex, sessionIndexForAPI, sessionIdForAPI, setCurrentSessionId, chatContent, setChatContent, currentAICharacter, apiAIModelName, setFocusInput, setRefreshChatSessions, setIsLoading, setErrorMsg, manageProgressText, mScrollToBottom
}) => {
  setIsLoading(true);
  manageProgressText("show", "Text");

  attachedImages.map(image => image.url)

  // Add the user message to chat content
  const userMessage = {
    message: userInput,
    isUserMessage: true,
    dateGenerate: formatDate(new Date().toISOString()),
    imageLocations: attachedImages.map(image => image.url),
    fileNames: attachedFiles.map(file => file.url)
  };
  const updatedChatContent = [...chatContent];
  if (config.VERBOSE_SUPERB === 1) {
    console.log("chatContent: ", chatContent)
    console.log("attachedFiles: ", attachedFiles)
  }
  // if it's not first message and ai_character is set - don't overwrite it (at the beginning we set it as assistant)
  if (!updatedChatContent[sessionIndexForAPI].ai_character_name || chatContent[sessionIndexForAPI].messages.length < 2)
    updatedChatContent[sessionIndexForAPI].ai_character_name = currentAICharacter

  // get current character (later we will check if auto response is set)
  const currentCharacter = characters.find(character => character.nameForAPI === currentAICharacter);

  // collect chat history (needed to send it API to get whole context of chat)
  // (excluding the latest message - as this will be sent via userPrompt), including images if any
  // or excluding 1 or 2 last messages - if its edited user message
  var chatHistory = chatContent[sessionIndexForAPI].messages;

  if (editMessagePosition !== null) {
    // if it is edited message - we have to drop 2 last messages (user and AI response)
    // but only if it is not the last message in chat
    if (editMessagePosition.index === chatHistory.length - 1) {
      chatHistory = chatHistory.slice(0, -1);
    } else {
      chatHistory = chatHistory.slice(0, -2);
    }
  }

  const finalUserInput = {
    "prompt": [
      { "type": "text", "text": userInput },
      ...attachedImages.map(image => ({ "type": "image_url", "image_url": { "url": image.url } })),
      ...attachedFiles.map(file => ({ "type": "file_url", "file_url": { "url": file.url } })),
    ],
    "chat_history": (chatHistory.map((message) => ({
      "role": message.isUserMessage ? "user" : "assistant",
      "content": [
        { "type": "text", "text": message.message },
        ...(message.imageLocations || []).map(imageUrl => ({ "type": "image_url", "image_url": { "url": imageUrl } })),
        ...(message.fileNames || []).map(url => ({ "type": "file_url", "file_url": { "url": url } }))
      ]
    }))),
  };

  // Add or replace user message
  if (editMessagePosition === null) {
    updatedChatContent[sessionIndexForAPI].messages.push(userMessage);
  } else {
    // Extract the URLs from attachedImages and attachedFile
    const imageUrls = attachedImages.map(image => image.url);
    const fileUrls = attachedFiles.map(file => file.url);
    updatedChatContent[sessionIndexForAPI].messages[editMessagePosition.index].message = userInput;
    updatedChatContent[sessionIndexForAPI].messages[editMessagePosition.index].imageLocations = imageUrls;
    updatedChatContent[sessionIndexForAPI].messages[editMessagePosition.index].fileNames = fileUrls;
  }
  setChatContent(updatedChatContent);

  // Buffer to hold the chunks until the message is complete
  let chunkBuffer = '';
  let aiMessageIndex;

  try {
    if (config.VERBOSE_SUPERB === 1) {
      console.log("API call. Final User Input", finalUserInput);
    }

    // most characters will have autoResponse - set to true - because we want them to respond (but there are exceptions)
    if (currentCharacter.autoResponse) {
      if (editMessagePosition === null) {
        // Add a placeholder for the AI message
        const aiMessagePlaceholder = {
          message: '',
          isUserMessage: false,
          apiAIModelName: apiAIModelName,
          dateGenerate: formatDate(new Date().toISOString()),
          imageLocations: [],
          aiCharacterName: currentAICharacter
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
            apiAIModelName: apiAIModelName,
            dateGenerate: formatDate(new Date().toISOString()),
            imageLocations: [],
            aiCharacterName: currentAICharacter
          };
          updatedChatContent[sessionIndexForAPI].messages.push(aiMessagePlaceholder);
        } else {
          // if exists - overwrite
          updatedChatContent[sessionIndexForAPI].messages[aiMessageIndex].message = '';
          updatedChatContent[sessionIndexForAPI].messages[aiMessageIndex].apiAIModelName = apiAIModelName;
          updatedChatContent[sessionIndexForAPI].messages[aiMessageIndex].dateGenerate = formatDate(new Date().toISOString());
        }
      }

      setChatContent(updatedChatContent);

      await apiMethods.triggerStreamingAPIRequest("chat", "text", "chat", finalUserInput, {
        onChunkReceived: (chunk) => {
          // if it's artgen and user disabled show prompt - don't show it
          if (currentAICharacter === "tools_artgen" && getImageArtgenShowPrompt() === false) {
            return
          }
          chunkBuffer += chunk;
          updatedChatContent[sessionIndexForAPI].messages[aiMessageIndex].message = chunkBuffer;
          setChatContent([...updatedChatContent]);
          mScrollToBottom(sessionIndexForAPI);
        },
        onStreamEnd: async (fullResponse) => {
          manageProgressText("hide", "Text");
          mScrollToBottom(sessionIndexForAPI);

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

              // refresh sidebar chat sessions (only once - when we have initial messages - not to keep refreshing all the time)
              if (chatContent[sessionIndexForAPI].messages.length < 3) {
                setRefreshChatSessions(true);
              }
            }
          });

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
                mScrollToBottom(sessionIndexForAPI);
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
    } else { // if its edited message
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

          // refresh sidebar chat sessions (only once - when we have initial messages - not to keep refreshing all the time)
          if (chatContent[sessionIndexForAPI].messages.length < 2) {
            setRefreshChatSessions(true);
          }
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

export default CallChatAPI;
