import { createContext, useState, useEffect } from "react";
import { AuthService } from "./services/auth.service";
import config from "./config";

const authService = new AuthService();

export const StateContext = createContext({
  // this is to track which action is selected (generate, crop, etc)
  selectedAction: null,
  setSelectedAction: () => {},
  
  // this is to track general category selected (text, image, etc)
  selectedCategory: null,
  setSelectedCategory: () => {},

  // this is to track assetInput... at beginning its empty
  // but then when user generates (or uploads) something - those generated assets become assetInput 
  // this is more like URLs of files (to be stored in DB, so later we know what was used to generate this specific asset)
  assetInput: [],
  setAssetInput: () => {},

  // as assetInput is to store input to generate current asset (for example original text which we just rewrited) 
  // aiAreaContent is used to store generated content and displayed mainly in WAAIArea
  aiAreaContent: [],
  setAiAreaContent: () => {},

  // so we have assetInput - listing all assets generated (like images, audio, etc)
  // many time its just 1 file - so index will always be 0
  // but sometimes there are multiple assets (like images)
  // so we want to know which one is selected by user
  // this will be used when we want to execute action on specific asset (like resize, etc)
  // and btw it will be used to switch between images (button left and right)
  assetIndex: 0,
  setAssetIndex: () => {},

  // this is to control if working area is shown or not - and also content depends on it
  // it is shown when user selects category button in main screen
  // if its not set - main buttons are shown on starting screen
  showWorkingArea: false,
  setShowWorkingArea: () => {},

  // this is to control if assistant area (bottom of screen) is shown or not
  showAssistantArea: false,
  setShowAssistantArea: () => {},

  // this will be used when generation starts
  // in AI Area - we will listen to changes to that - and hide or show spinner
  // there is also exception in HumanMedia - because with generationInProgress set - we will also hide prompt area
  generationInProgress: false,
  setGenerationInProgress: () => {},

  // similar as above - we will listen to it and show / hide different kinds of elements
  // AI area, Human Area (media nand input)
  generationCompleted: false,
  setGenerationCompleted: () => {},

  // this is to show errors
  errorMsg: "",
  setErrorMsg: () => {},

  // this is to track if user is logged in or not
  isLoggedIn: false,
  setIsLoggedIn: () => {},

  // this is to track customer id
  customerId: null,

  // if user is using mobile
  isMobile: false,
  setIsMobile: () => {},

  // if we use bluetooth (doesn't work on mobile :( )
  useBluetooth: true,
  setUseBluetooth: () => {},
});

export const StateContextProvider = ({ children }) => {
  const [selectedAction, setSelectedAction] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [assetInput, setAssetInput] = useState([]);
  const [aiAreaContent, setAiAreaContent] = useState([]);
  const [assetIndex, setAssetIndex] = useState(0);
  const [showWorkingArea, setShowWorkingArea] = useState(false);
  const [showAssistantArea, setShowAssistantArea] = useState(false);
  const [generationInProgress, setGenerationInProgress] = useState(false);
  const [generationCompleted, setGenerationCompleted] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [customerId, setCustomerId] = useState(null);
  const [useBluetooth, setUseBluetooth] = useState(false);

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (currentUser && currentUser.accessToken) {
      setIsLoggedIn(true);
      setCustomerId(currentUser.userId);
    }

    // check if mobile - to show/hide some elements
    if (window.innerWidth <= 768) {
      setIsMobile(true);
    }
  }, []);

  const logout = () => {
    authService.logout();
    setIsLoggedIn(false);
    setCustomerId(0);
  };

  const setUserSettings = (settings) => {
    if (settings) {
      userSettings = settings;
      // save to local storage
      localStorage.setItem(
        "userSettings",
        JSON.stringify({ userSettings })
      );
    }
  };

  let userSettings = config.userSettings;
  // update from local storage
  const userSettingsFromStorage = localStorage.getItem('userSettings');
  if (userSettingsFromStorage) {
    userSettings = JSON.parse(userSettingsFromStorage)['userSettings'];
  }
  userSettings['isMobile'] = isMobile;
  if (isMobile) {
    userSettings.text.textGenStreaming = false;
  }

  return (
    <StateContext.Provider
      value={{
        selectedAction, setSelectedAction,
        selectedCategory, setSelectedCategory,
        assetInput, setAssetInput,
        aiAreaContent, setAiAreaContent,
        assetIndex, setAssetIndex,
        showWorkingArea, setShowWorkingArea,
        showAssistantArea, setShowAssistantArea,
        generationInProgress, setGenerationInProgress,
        generationCompleted, setGenerationCompleted,
        errorMsg, setErrorMsg,
        isLoggedIn, setIsLoggedIn,
        customerId, logout,
        userSettings, setUserSettings,
        isMobile, setIsMobile,
        useBluetooth, setUseBluetooth,
      }}
    >
      {children}
    </StateContext.Provider>
  );
};