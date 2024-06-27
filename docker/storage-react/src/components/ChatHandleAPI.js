// ChatHandleAPI.js
import config from '../config';
import apiMethods from '../services/api.methods';
import { getTextAICharacter, getImageArtgenShowPrompt, getImageAutoGenerateImage } from '../utils/configuration';

const ChatHandleAPI = async ({
  userInput, attachedImages, currentSessionIndex, currentSessionId, chatContent, setChatContent, setIsLoading, setErrorMsg, manageProgressText
}) => {
  setIsLoading(true);
  manageProgressText("show", "Text")
  const sessionIdForAPI = currentSessionId;

  // Add the user message to chat content
  const userMessage = { message: userInput, isUserMessage: true, imageLocations: attachedImages.map(image => image.url) };
  const updatedChatContent = [...chatContent];
  updatedChatContent[currentSessionIndex].messages.push(userMessage);
  setChatContent(updatedChatContent);

  // prepare user input for API call
  const finalUserInput = {
    "prompt": [
      { "type": "text", "text": userInput },
      ...attachedImages.map(image => ({ "type": "image_url", "image_url": { "url": image.url } }))
    ],
    "chat_history": (chatContent[currentSessionIndex].messages || []).map((message) => ({
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

  updatedChatContent[currentSessionIndex].messages.push(aiMessagePlaceholder);
  aiMessageIndex = updatedChatContent[currentSessionIndex].messages.length - 1;
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

        updatedChatContent[currentSessionIndex].messages[aiMessageIndex].message = chunkBuffer;
        setChatContent([...updatedChatContent]);
      },
      onStreamEnd: async (fullResponse) => {
        manageProgressText("hide", "Text")

        // for artgen mode - if image is enabled and no images attached - generate image
        if (getTextAICharacter() === "tools_artgen" && getImageAutoGenerateImage() && attachedImages.length === 0) {
          manageProgressText("show", "Image")
          const userInput = { "text": fullResponse };
          await apiMethods.triggerAPIRequest("generate", "image", "generate", userInput).then((response) => {
            if (response.success) {
              updatedChatContent[currentSessionIndex].messages[aiMessageIndex].imageLocations = [response.message.result];
              setChatContent([...updatedChatContent]);
              manageProgressText("hide", "Image")
            } else {
              setErrorMsg("Problem generating image");
              manageProgressText("hide", "Image")
            }
          });
        }

        // save to DB
        /*const currentUserMessage = userInput
        const currentAIResponse = fullResponse
        
        await apiMethods.triggerAPIRequest("api/db", "provider.db", "db_new_message", userInput).then((response) => {
          if (response.success) {
          } else {
            setErrorMsg("Problem saving in DB");
          }
        });
        */



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
