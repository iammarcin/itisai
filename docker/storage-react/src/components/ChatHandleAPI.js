// ChatHandleAPI.js
import apiMethods from '../services/api.methods';
import { getTextAICharacter } from '../utils/local.storage';

const ChatHandleAPI = async ({
 userInput, attachedImages, chatContent, setChatContent, setIsLoading
}) => {
 setIsLoading(true);

 // Add the user message to chat content
 setChatContent(prevContent => [
  ...(prevContent || []),
  { message: userInput, isUserMessage: true }
 ]);

 const finalUserInput = {
  "prompt": [
   { "type": "text", "text": userInput },
   //...attachedImages.map(image => ({ "type": "image_url", "image_url": { "url": URL.createObjectURL(image) } }))
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
  console.log("Api call to be executed!")
  console.log("Final User Input", finalUserInput);
  await apiMethods.triggerStreamingAPIRequest("chat", "text", "chat", finalUserInput, {
   onChunkReceived: (chunk) => {
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
   }
  });
 } catch (error) {
  setIsLoading(false);
  console.error('Error during streaming:', error);
 }
}

export default ChatHandleAPI;
