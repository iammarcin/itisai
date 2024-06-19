// ChatHandleAPI.js
import config from '../config';
import apiMethods from '../services/api.methods';
import { getTextAICharacter, getImageArtgenShowPrompt, getImageAutoGenerateImage } from '../utils/configuration';

const ChatHandleAPI = async ({
 userInput, attachedImages, chatContent, setChatContent, setIsLoading, setErrorMsg
}) => {
 setIsLoading(true);

 // Add the user message to chat content
 setChatContent(prevContent => [
  ...(prevContent || []),
  { message: userInput, isUserMessage: true, imageLocations: attachedImages.map(image => image.url) }
 ]);

 const finalUserInput = {
  "prompt": [
   { "type": "text", "text": userInput },
   ...attachedImages.map(image => ({ "type": "image_url", "image_url": { "url": image.url } }))
  ],
  "chat_history": (chatContent || []).map((message) => ({
   "role": message.isUserMessage ? "user" : "assistant",
   "content": [
    { "type": "text", "text": message.message },
    ...(message.imageLocations || []).map(imageUrl => ({ "type": "image_url", "image_url": { "url": imageUrl } }))
   ]
  }))
 };

 // Buffer to hold the chunks until the message is complete
 let chunkBuffer = '';
 try {
  if (config.DEBUG === 1) {
   console.log("Api call to be executed!")
   console.log("Final User Input", finalUserInput);
  }
  await apiMethods.triggerStreamingAPIRequest("chat", "text", "chat", finalUserInput, {
   onChunkReceived: (chunk) => {
    if (getTextAICharacter() === "tools_artgen" && getImageArtgenShowPrompt === false) {
     return
    }
    chunkBuffer += chunk;

    setChatContent(prevContent => {
     const newContent = [...(prevContent || [])];
     const lastMessage = newContent[newContent.length - 1];
     // overwrite message (chunk)
     if (lastMessage && !lastMessage.isUserMessage) {
      lastMessage.message = chunkBuffer;
      lastMessage.aiCharacterName = getTextAICharacter()
     } else {
      // or start writing chunk
      newContent.push({
       message: chunkBuffer,
       isUserMessage: false,
       aiCharacterName: getTextAICharacter()
      });
     }
     return newContent;
    });
   },
   onStreamEnd: () => {
    setIsLoading(false);
    if (getTextAICharacter() === "tools_artgen" && getImageAutoGenerateImage() && attachedImages.length === 0) {
     setErrorMsg("generating image")
    }

   }
  });
 } catch (error) {
  setIsLoading(false);
  setErrorMsg("Error during streaming. Try again.")
  console.error('Error during streaming:', error);
 }
}

export default ChatHandleAPI;
