import { useContext, useCallback } from 'react';
import { StateContext } from '../components/StateContextProvider';

import CallChatAPI from '../services/call.chat.api';

import { getTextAICharacter, getTextModelName } from '../utils/configuration';

// generate text API call (and potentially image)
// if editMessagePosition is not null - it means it is edited message
const useChatAPI = () => {
  const {
    chatContent, setChatContent, assetInput, attachedImages, attachedFiles, currentSessionIndex, currentSessionId,
    setCurrentSessionId, userInput, setFocusInput, setRefreshChatSessions, setIsLoading, setErrorMsg,
    setShowCharacterSelection, manageProgressText, mScrollToBottom
  } = useContext(StateContext);

  const callChatAPI = useCallback(async (editMessagePosition = null) => {
    setShowCharacterSelection(false);
    setErrorMsg('');

    try {
      const sessionIdForAPI = currentSessionId;
      const sessionIndexForAPI = currentSessionIndex;
      const currentAICharacter = getTextAICharacter();
      const apiAIModelName = getTextModelName();

      await CallChatAPI({
        userInput, assetInput, editMessagePosition, attachedImages, attachedFiles, currentSessionIndex,
        sessionIndexForAPI, sessionIdForAPI, setCurrentSessionId, chatContent, setChatContent,
        currentAICharacter, apiAIModelName, setFocusInput, setRefreshChatSessions, setIsLoading,
        setErrorMsg, manageProgressText, mScrollToBottom
      });
    } catch (error) {
      setErrorMsg(error.message);
    }
  }, [userInput, assetInput, attachedFiles, attachedImages, chatContent, currentSessionId, currentSessionIndex, manageProgressText, mScrollToBottom, setChatContent, setCurrentSessionId, setErrorMsg, setFocusInput, setIsLoading, setRefreshChatSessions, setShowCharacterSelection]);

  return { callChatAPI };
};

export default useChatAPI;
