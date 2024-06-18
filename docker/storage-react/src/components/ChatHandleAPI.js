// ChatHandleAPI.js
import apiMethods from '../services/api.methods';

const ChatHandleAPI = async ({
 userInput, chatContent, setChatContent, setIsLoading
}) => {
 setIsLoading(true);

 // Add the user message to chat content
 setChatContent(prevContent => [
  ...prevContent,
  { message: userInput, isUserMessage: true }
 ]);

 const finalUserInput = {
  "prompt": [{ "type": "text", "text": userInput }],
  "chat_history": chatContent.map((message) => ({
   "role": message.isUserMessage ? "user" : "assistant",
   "content": [{ "type": "text", "text": message.message }]
  }))
 }

 // Buffer to hold the chunks until the message is complete
 let chunkBuffer = '';
 try {
  await apiMethods.triggerStreamingAPIRequest("chat", "text", "chat", finalUserInput, {
   onChunkReceived: (chunk) => {
    console.log("Chunk received:", chunk)
    chunkBuffer += chunk;

    setChatContent(prevContent => {
     const newContent = [...prevContent];
     const lastMessage = newContent[newContent.length - 1];
     if (lastMessage && !lastMessage.isUserMessage) {
      lastMessage.message = chunkBuffer;
     } else {
      newContent.push({ message: chunkBuffer, isUserMessage: false });
     }
     return newContent;
    });
   },
   onStreamEnd: () => {
    console.log("Stream end")
    setIsLoading(false);
   }
  });
 } catch (error) {
  setIsLoading(false);
  console.error('Error during streaming:', error);
 }
}

export default ChatHandleAPI;
