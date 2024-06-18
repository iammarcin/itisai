// ChatHandleAPI.js
import apiMethods from '../services/api.methods';

const ChatHandleAPI = async ({
 userInput, chatContent, setChatContent
}) => {

 const finalUserInput = {
  "prompt": [{ "type": "text", "text": userInput }],
  "chat_history": chatContent.map((message) => ({
   "role": message.isUserMessage ? "user" : "assistant",
   "content": [{ "type": "text", "text": message.message }]
  }))
 }
 await apiMethods.triggerStreamingAPIRequest("chat", "text", "chat", finalUserInput);

}

export default ChatHandleAPI;
