// StateContextProvider.js

import { createContext, useState, useEffect, useRef, useCallback } from "react";

export const StateContext = createContext();

export const StateContextProvider = ({ children }) => {
  // chat content from chat window
  const [chatContent, setChatContent] = useState([
    {
      id: 0,
      messages: [] // Each session starts with an empty array of messages
    }
  ]);
  // optional assetInput - used for example in Health - it is separated from chatContent - because we don't necessarily want it to be displayed for user in chat messages (it's long etc)
  const [assetInput, setAssetInput] = useState([]);
  // this is index of sessions on top menu (in circle buttons) - to identify which button is currently active etc
  const [currentSessionIndex, setCurrentSessionIndex] = useState(0);
  // this is to track current session Id - from DB
  const [currentSessionId, setCurrentSessionId] = useState(null);
  // this is to trigger fetch session in ChatWindow - this together with shouldSkipSessionFetching - will determine if we should fetchChatContent or not
  const [fetchSessionId, setFetchSessionId] = useState(null);
  // used in tandem with above - it will be set to false in most cases (by default so when user just provides URL, or when we click on Sidebar and we want session to be fetched) 
  // but sometimes will be set to true (for example in TopMenu when clicking between sessions) - because then we just want to navigate to URL but don't want sessions to be fetched (because they are already there)
  const [shouldSkipSessionFetching, setShouldSkipSessionFetching] = useState(false);
  // show window with characters
  const [showCharacterSelection, setShowCharacterSelection] = useState(true);
  // this will be used to focus (make active) userInput text area from BottomToolsMenu - so i don't need to click on it to start typing
  const [focusInput, setFocusInput] = useState(false);
  // this is when we click regenerate in ChatMessage - we have to use useEffect here - because other way async data is not set before sending to API
  const [readyForRegenerate, setReadyForRegenerate] = useState(false);
  // this will be used to force refresh of chat sessions in Sidebar (when new session is created)
  const [refreshChatSessions, setRefreshChatSessions] = useState(false);
  // progress bar handling
  const [progressBarMessage, setProgressBarMessage] = useState('');
  // user input (text + images) from bottom menu
  const [userInput, setUserInput] = useState('');
  // used for editing messages
  const [editingMessage, setEditingMessage] = useState(null);
  const [attachedImages, setAttachedImages] = useState([]);
  const [attachedFiles, setAttachedFiles] = useState([]);
  // (from ChatWindow) this is used for scrollToBottom
  const endOfMessagesRef = useRef(null);
  // this is to avoid fetchChatContent on changing of currentSessionIndex (when switching top menu sessions) - IMPORTANT! 
  // and also for scrollToBottom function (to be sure that we're scrolling if we are generating data from APIs in active session only)
  const currentSessionIndexRef = useRef(currentSessionIndex);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  // to control UI depending if its mobile or not
  const [isMobile, setIsMobile] = useState(false);
  // used in Sidebar - search text is what we put into search text input in sidebar
  // it is also reset when new chat is clicked
  const [sidebarSearchText, setSidebarSearchText] = useState('');

  // this is showProgress, hideProgress merged in one place
  // accepting method - "show" and "hide"
  // and then adding or removing specific text
  const manageProgressText = (method, text) => {
    if (method === 'show') {
      setProgressBarMessage((prevMessage) => prevMessage ? `${prevMessage} ${text}` : text);
    } else if (method === 'hide') {
      setProgressBarMessage((prevMessage) => {
        const messages = prevMessage.split(' ');
        const filteredMessages = messages.filter((msg) => msg !== text);
        return filteredMessages.join(' ');
      });
    }
  }

  const scrollToBottom = (whichChat, smooth = true) => {
    if (whichChat === currentSessionIndexRef.current && endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({
        behavior: smooth ? 'smooth' : 'auto',
      });
    }
  };

  useEffect(() => {
    // check if mobile - to arrange UI
    if (window.innerWidth <= 768) {
      setIsMobile(true);
    }
  }, []);

  // a memoized version of scroll to bottom (not to trigger re-renders)
  const mScrollToBottom = useCallback((whichChat, smooth = true) => {
    scrollToBottom(whichChat, smooth);
  }, []);

  /*
  // function put outside of Main component - because it triggered re-renders from different places
  const scrollToBottom = (whichChat, smooth = true, endOfMessagesRef, currentSessionIndexRef) => {
    if (whichChat === currentSessionIndexRef.current) {
      // smooth not needed - for example when restoring session
      var behavior = 'auto';
      if (smooth)
        behavior = 'smooth';
      endOfMessagesRef.current.scrollIntoView({
        behavior: behavior,
      });
    }

    // a memoized version of scroll to bottom (not to trigger re-renders)
    const mScrollToBottom = useCallback((whichChat, smooth = true) => {
      scrollToBottom(whichChat, smooth, endOfMessagesRef, currentSessionIndexRef);
    }, [endOfMessagesRef, currentSessionIndexRef]);

    */


  // i tried few different methods - didn't really work well
  /*const chatWindowContainer = document.querySelector('.bottom-tools-menu');
  const isAtBottom = chatWindowContainer.scrollHeight - chatWindowContainer.scrollTop <= chatWindowContainer.clientHeight + 70;
  console.log("isAtBottom: ", isAtBottom);*/
  /*if (isAtBottom) {
    console.log("scrolling to bottom")
 
    console.log(whichChat)
    console.log(currentSessionIndexRef.current)
    if (whichChat === currentSessionIndexRef.current) {
      console.log("scrolling to bottom2")
      //const scrollTargetPosition = botTextAreaContainer.getBoundingClientRect().top - window.innerHeight + botTextAreaContainer.offsetHeight;
 
      // Scroll smoothly to the target position
      /*window.scrollBy({
        top: chatWindowContainer.getBoundingClientRect().bottom,
        behavior: 'smooth',
      });*/
  /*endOfMessagesRef.current.scrollIntoView({
    behavior: 'smooth',
  });
}
}
};*/

  return (
    <StateContext.Provider value={{
      chatContent, setChatContent,
      assetInput, setAssetInput,
      currentSessionIndex, setCurrentSessionIndex,
      currentSessionId, setCurrentSessionId,
      fetchSessionId, setFetchSessionId,
      shouldSkipSessionFetching, setShouldSkipSessionFetching,
      showCharacterSelection, setShowCharacterSelection,
      focusInput, setFocusInput,
      readyForRegenerate, setReadyForRegenerate,
      refreshChatSessions, setRefreshChatSessions,
      progressBarMessage, setProgressBarMessage,
      userInput, setUserInput,
      editingMessage, setEditingMessage,
      attachedImages, setAttachedImages,
      attachedFiles, setAttachedFiles,
      endOfMessagesRef, currentSessionIndexRef,
      isLoading, setIsLoading,
      errorMsg, setErrorMsg,
      isMobile,
      sidebarSearchText, setSidebarSearchText,
      manageProgressText, mScrollToBottom,
    }}>
      {children}
    </StateContext.Provider>
  );
};
