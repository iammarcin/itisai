// ChatHandleAPI.js
import apiMethods from '../services/api.methods';
import { getTextAICharacter } from '../utils/local.storage';

const ChatHandleAPI = async ({
 userInput, chatContent, setChatContent, setIsLoading
}) => {
 console.log("NNNN")
 setIsLoading(true);


 // Add the user message to chat content
 setChatContent(prevContent => [
  ...(prevContent || []),
  { message: userInput, isUserMessage: true }
 ]);

 console.log("NNNN12");
 const finalUserInput = {
  "prompt": [{ "type": "text", "text": userInput }],
  "chat_history": (chatContent || []).map((message) => ({
   "role": message.isUserMessage ? "user" : "assistant",
   "content": [{ "type": "text", "text": message.message }]
  }))
 }
 console.log("NNNN123");
 // Buffer to hold the chunks until the message is complete
 let chunkBuffer = '';
 try {
  console.log("AAAA")
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
