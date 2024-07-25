// FloatingChat.js

import React, { useState, useEffect, useContext } from 'react';

import { StateContext } from '../StateContextProvider';
import useChatAPI from '../../hooks/useChatAPI';

import { setTextAICharacter, getTextModelName } from '../../utils/configuration';

import { ResizableBox } from 'react-resizable';
import 'react-resizable/css/styles.css';
import './css/FloatingChat.css';

import BottomToolsMenu from '../BottomToolsMenu';
import ChatMessage from '../ChatMessage';
import config from '../../config';

const FloatingChat = ({ data }) => {
  const {
    userInput, setUserInput, //chatContent, setChatContent,
    attachedImages, setAttachedImages,
    setAttachedFiles, editingMessage,
    errorMsg, setErrorMsg, isMobile,
  } = useContext(StateContext);

  const [chatContent, setChatContent] = useState([
    {
      "id": 0,
      "messages": [
        {
          "message": "[{\"id\":605,\"customer_id\":1,\"calendar_date\":\"2024-07-18\",\"sleep_time_seconds\":22440,\"sleep_start\":\"02:17\",\"sleep_end\":\"08:31\",\"nap_time_seconds\":0,\"nap_data\":null,\"deep_sleep_seconds\":3720,\"light_sleep_seconds\":9840,\"rem_sleep_seconds\":8880,\"awake_sleep_seconds\":0,\"average_respiration_value\":17,\"lowest_respiration_value\":13,\"highest_respiration_value\":21,\"awake_count\":0,\"avg_sleep_stress\":20,\"sleep_score_feedback\":\"POSITIVE_CONTINUOUS\",\"sleep_score_insight\":\"POSITIVE_LATE_BED_TIME\",\"sleep_score_personalized_insight\":\"GENERAL_POS_FAIR_OR_POOR_SLEEP\",\"overall_score_value\":73,\"overall_score_qualifier\":\"FAIR\",\"total_duration_qualifier\":\"FAIR\",\"stress_qualifier\":\"FAIR\",\"awake_count_qualifier\":\"EXCELLENT\",\"rem_percentage_value\":40,\"rem_percentage_qualifier\":\"FAIR\",\"rem_optimal_start\":21,\"rem_optimal_end\":31,\"restlessness_qualifier\":\"EXCELLENT\",\"restlessness_optimal_start\":0,\"restlessness_optimal_end\":5,\"light_percentage_value\":44,\"light_percentage_qualifier\":\"EXCELLENT\",\"light_optimal_start\":30,\"light_optimal_end\":64,\"deep_percentage_value\":17,\"deep_percentage_qualifier\":\"GOOD\",\"deep_optimal_start\":16,\"deep_optimal_end\":33,\"avg_overnight_hrv\":40,\"resting_heart_rate\":48,\"body_battery_change\":41,\"restless_moments_count\":21},{\"id\":610,\"customer_id\":1,\"calendar_date\":\"2024-07-19\",\"sleep_time_seconds\":28260,\"sleep_start\":\"22:09\",\"sleep_end\":\"06:07\",\"nap_time_seconds\":0,\"nap_data\":null,\"deep_sleep_seconds\":5640,\"light_sleep_seconds\":18900,\"rem_sleep_seconds\":3720,\"awake_sleep_seconds\":420,\"average_respiration_value\":17,\"lowest_respiration_value\":13,\"highest_respiration_value\":20,\"awake_count\":1,\"avg_sleep_stress\":18,\"sleep_score_feedback\":\"POSITIVE_LONG_AND_DEEP\",\"sleep_score_insight\":\"NONE\",\"sleep_score_personalized_insight\":\"STRESS_POS_EXCELLENT_OR_GOOD_SLEEP_VERY_RESTFUL_DAY\",\"overall_score_value\":85,\"overall_score_qualifier\":\"GOOD\",\"total_duration_qualifier\":\"EXCELLENT\",\"stress_qualifier\":\"FAIR\",\"awake_count_qualifier\":\"EXCELLENT\",\"rem_percentage_value\":13,\"rem_percentage_qualifier\":\"FAIR\",\"rem_optimal_start\":21,\"rem_optimal_end\":31,\"restlessness_qualifier\":\"EXCELLENT\",\"restlessness_optimal_start\":0,\"restlessness_optimal_end\":5,\"light_percentage_value\":67,\"light_percentage_qualifier\":\"FAIR\",\"light_optimal_start\":30,\"light_optimal_end\":64,\"deep_percentage_value\":20,\"deep_percentage_qualifier\":\"EXCELLENT\",\"deep_optimal_start\":16,\"deep_optimal_end\":33,\"avg_overnight_hrv\":48,\"resting_heart_rate\":43,\"body_battery_change\":56,\"restless_moments_count\":26},{\"id\":611,\"customer_id\":1,\"calendar_date\":\"2024-07-20\",\"sleep_time_seconds\":17940,\"sleep_start\":\"02:36\",\"sleep_end\":\"07:42\",\"nap_time_seconds\":0,\"nap_data\":null,\"deep_sleep_seconds\":7140,\"light_sleep_seconds\":8220,\"rem_sleep_seconds\":2580,\"awake_sleep_seconds\":420,\"average_respiration_value\":17,\"lowest_respiration_value\":14,\"highest_respiration_value\":22,\"awake_count\":0,\"avg_sleep_stress\":16,\"sleep_score_feedback\":\"POSITIVE_SHORT_BUT_DEEP\",\"sleep_score_insight\":\"POSITIVE_LATE_BED_TIME\",\"sleep_score_personalized_insight\":\"STRESS_POS_FAIR_OR_POOR_SLEEP_RESTFUL_DAY\",\"overall_score_value\":64,\"overall_score_qualifier\":\"FAIR\",\"total_duration_qualifier\":\"POOR\",\"stress_qualifier\":\"FAIR\",\"awake_count_qualifier\":\"EXCELLENT\",\"rem_percentage_value\":14,\"rem_percentage_qualifier\":\"FAIR\",\"rem_optimal_start\":21,\"rem_optimal_end\":31,\"restlessness_qualifier\":\"EXCELLENT\",\"restlessness_optimal_start\":0,\"restlessness_optimal_end\":5,\"light_percentage_value\":46,\"light_percentage_qualifier\":\"EXCELLENT\",\"light_optimal_start\":30,\"light_optimal_end\":64,\"deep_percentage_value\":40,\"deep_percentage_qualifier\":\"EXCELLENT\",\"deep_optimal_start\":16,\"deep_optimal_end\":33,\"avg_overnight_hrv\":49,\"resting_heart_rate\":46,\"body_battery_change\":50,\"restless_moments_count\":16},{\"id\":612,\"customer_id\":1,\"calendar_date\":\"2024-07-21\",\"sleep_time_seconds\":31080,\"sleep_start\":\"22:17\",\"sleep_end\":\"07:03\",\"nap_time_seconds\":0,\"nap_data\":null,\"deep_sleep_seconds\":5580,\"light_sleep_seconds\":15420,\"rem_sleep_seconds\":10080,\"awake_sleep_seconds\":480,\"average_respiration_value\":17,\"lowest_respiration_value\":13,\"highest_respiration_value\":20,\"awake_count\":1,\"avg_sleep_stress\":18,\"sleep_score_feedback\":\"POSITIVE_LONG_AND_CALM\",\"sleep_score_insight\":\"POSITIVE_RESTFUL_DAY\",\"sleep_score_personalized_insight\":\"STRESS_POS_EXCELLENT_OR_GOOD_SLEEP_RESTFUL_DAY\",\"overall_score_value\":87,\"overall_score_qualifier\":\"GOOD\",\"total_duration_qualifier\":\"EXCELLENT\",\"stress_qualifier\":\"FAIR\",\"awake_count_qualifier\":\"EXCELLENT\",\"rem_percentage_value\":32,\"rem_percentage_qualifier\":\"FAIR\",\"rem_optimal_start\":21,\"rem_optimal_end\":31,\"restlessness_qualifier\":\"EXCELLENT\",\"restlessness_optimal_start\":0,\"restlessness_optimal_end\":5,\"light_percentage_value\":50,\"light_percentage_qualifier\":\"EXCELLENT\",\"light_optimal_start\":30,\"light_optimal_end\":64,\"deep_percentage_value\":18,\"deep_percentage_qualifier\":\"EXCELLENT\",\"deep_optimal_start\":16,\"deep_optimal_end\":33,\"avg_overnight_hrv\":44,\"resting_heart_rate\":46,\"body_battery_change\":62,\"restless_moments_count\":25},{\"id\":613,\"customer_id\":1,\"calendar_date\":\"2024-07-22\",\"sleep_time_seconds\":35340,\"sleep_start\":\"21:47\",\"sleep_end\":\"07:55\",\"nap_time_seconds\":0,\"nap_data\":null,\"deep_sleep_seconds\":4680,\"light_sleep_seconds\":21180,\"rem_sleep_seconds\":9480,\"awake_sleep_seconds\":1140,\"average_respiration_value\":17,\"lowest_respiration_value\":11,\"highest_respiration_value\":22,\"awake_count\":1,\"avg_sleep_stress\":21,\"sleep_score_feedback\":\"POSITIVE_LONG_AND_REFRESHING\",\"sleep_score_insight\":\"NONE\",\"sleep_score_personalized_insight\":\"GENERAL_POS_EXCELLENT_OR_GOOD_SLEEP\",\"overall_score_value\":84,\"overall_score_qualifier\":\"GOOD\",\"total_duration_qualifier\":\"EXCELLENT\",\"stress_qualifier\":\"FAIR\",\"awake_count_qualifier\":\"GOOD\",\"rem_percentage_value\":27,\"rem_percentage_qualifier\":\"EXCELLENT\",\"rem_optimal_start\":21,\"rem_optimal_end\":31,\"restlessness_qualifier\":\"GOOD\",\"restlessness_optimal_start\":0,\"restlessness_optimal_end\":5,\"light_percentage_value\":60,\"light_percentage_qualifier\":\"GOOD\",\"light_optimal_start\":30,\"light_optimal_end\":64,\"deep_percentage_value\":13,\"deep_percentage_qualifier\":\"FAIR\",\"deep_optimal_start\":16,\"deep_optimal_end\":33,\"avg_overnight_hrv\":40,\"resting_heart_rate\":47,\"body_battery_change\":56,\"restless_moments_count\":46},{\"id\":615,\"customer_id\":1,\"calendar_date\":\"2024-07-23\",\"sleep_time_seconds\":35160,\"sleep_start\":\"21:51\",\"sleep_end\":\"08:01\",\"nap_time_seconds\":0,\"nap_data\":null,\"deep_sleep_seconds\":5640,\"light_sleep_seconds\":18000,\"rem_sleep_seconds\":11520,\"awake_sleep_seconds\":1440,\"average_respiration_value\":17,\"lowest_respiration_value\":12,\"highest_respiration_value\":21,\"awake_count\":2,\"avg_sleep_stress\":19,\"sleep_score_feedback\":\"POSITIVE_LONG_AND_CALM\",\"sleep_score_insight\":\"NONE\",\"sleep_score_personalized_insight\":\"STRESS_POS_EXCELLENT_OR_GOOD_SLEEP_RESTFUL_DAY\",\"overall_score_value\":82,\"overall_score_qualifier\":\"GOOD\",\"total_duration_qualifier\":\"EXCELLENT\",\"stress_qualifier\":\"FAIR\",\"awake_count_qualifier\":\"FAIR\",\"rem_percentage_value\":33,\"rem_percentage_qualifier\":\"FAIR\",\"rem_optimal_start\":21,\"rem_optimal_end\":31,\"restlessness_qualifier\":\"FAIR\",\"restlessness_optimal_start\":0,\"restlessness_optimal_end\":5,\"light_percentage_value\":51,\"light_percentage_qualifier\":\"EXCELLENT\",\"light_optimal_start\":30,\"light_optimal_end\":64,\"deep_percentage_value\":16,\"deep_percentage_qualifier\":\"GOOD\",\"deep_optimal_start\":16,\"deep_optimal_end\":33,\"avg_overnight_hrv\":45,\"resting_heart_rate\":44,\"body_battery_change\":57,\"restless_moments_count\":53},{\"id\":616,\"customer_id\":1,\"calendar_date\":\"2024-07-24\",\"sleep_time_seconds\":22320,\"sleep_start\":\"22:32\",\"sleep_end\":\"05:18\",\"nap_time_seconds\":0,\"nap_data\":null,\"deep_sleep_seconds\":4980,\"light_sleep_seconds\":14880,\"rem_sleep_seconds\":2460,\"awake_sleep_seconds\":2040,\"average_respiration_value\":17,\"lowest_respiration_value\":12,\"highest_respiration_value\":21,\"awake_count\":2,\"avg_sleep_stress\":16,\"sleep_score_feedback\":\"POSITIVE_DEEP\",\"sleep_score_insight\":\"NONE\",\"sleep_score_personalized_insight\":\"STRESS_POS_FAIR_OR_POOR_SLEEP_RESTFUL_DAY\",\"overall_score_value\":74,\"overall_score_qualifier\":\"FAIR\",\"total_duration_qualifier\":\"FAIR\",\"stress_qualifier\":\"FAIR\",\"awake_count_qualifier\":\"FAIR\",\"rem_percentage_value\":11,\"rem_percentage_qualifier\":\"FAIR\",\"rem_optimal_start\":21,\"rem_optimal_end\":31,\"restlessness_qualifier\":\"FAIR\",\"restlessness_optimal_start\":0,\"restlessness_optimal_end\":5,\"light_percentage_value\":67,\"light_percentage_qualifier\":\"FAIR\",\"light_optimal_start\":30,\"light_optimal_end\":64,\"deep_percentage_value\":22,\"deep_percentage_qualifier\":\"EXCELLENT\",\"deep_optimal_start\":16,\"deep_optimal_end\":33,\"avg_overnight_hrv\":53,\"resting_heart_rate\":45,\"body_battery_change\":53,\"restless_moments_count\":30},{\"id\":617,\"customer_id\":1,\"calendar_date\":\"2024-07-25\",\"sleep_time_seconds\":26520,\"sleep_start\":\"21:23\",\"sleep_end\":\"05:13\",\"nap_time_seconds\":0,\"nap_data\":null,\"deep_sleep_seconds\":6480,\"light_sleep_seconds\":16020,\"rem_sleep_seconds\":4020,\"awake_sleep_seconds\":1680,\"average_respiration_value\":17,\"lowest_respiration_value\":13,\"highest_respiration_value\":21,\"awake_count\":3,\"avg_sleep_stress\":23,\"sleep_score_feedback\":\"POSITIVE_LONG_AND_DEEP\",\"sleep_score_insight\":\"NONE\",\"sleep_score_personalized_insight\":\"STRESS_POS_FAIR_OR_POOR_SLEEP_RESTFUL_DAY\",\"overall_score_value\":78,\"overall_score_qualifier\":\"FAIR\",\"total_duration_qualifier\":\"EXCELLENT\",\"stress_qualifier\":\"FAIR\",\"awake_count_qualifier\":\"FAIR\",\"rem_percentage_value\":15,\"rem_percentage_qualifier\":\"FAIR\",\"rem_optimal_start\":21,\"rem_optimal_end\":31,\"restlessness_qualifier\":\"FAIR\",\"restlessness_optimal_start\":0,\"restlessness_optimal_end\":5,\"light_percentage_value\":60,\"light_percentage_qualifier\":\"GOOD\",\"light_optimal_start\":30,\"light_optimal_end\":64,\"deep_percentage_value\":24,\"deep_percentage_qualifier\":\"EXCELLENT\",\"deep_optimal_start\":16,\"deep_optimal_end\":33,\"avg_overnight_hrv\":48,\"resting_heart_rate\":48,\"body_battery_change\":51,\"restless_moments_count\":27}]\ngive me report",
          "isUserMessage": true,
          "dateGenerate": "2024-07-25 14:21",
          "imageLocations": [],
          "fileNames": [],
          "messageId": 1532
        },
        {
          "message": "Here's a summary report of your sleep data from July 18 to July 25, 2024. This report includes key metrics, insights, and overall trends observed during this period.\n\n### Sleep Summary Report\n\n#### Overview\n- **Total Duration of Sleep**: Ranged from 4 hours 59 minutes to 9 hours 15 minutes.\n- **Average Sleep Score**: 76.25 (Fair to Good)\n- **Average Sleep Duration**: Approximately 7 hours 15 minutes per night.\n- **Total Days Analyzed**: 8\n\n#### Daily Breakdown\n\n| Date       | Sleep Start | Sleep End | Total Sleep (hrs) | Deep Sleep (hrs) | Light Sleep (hrs) | REM Sleep (hrs) | Sleep Score | Overall Qualifier |\n|------------|-------------|-----------|--------------------|-------------------|-------------------|------------------|-------------|--------------------|\n| 2024-07-18 | 02:17       | 08:31     | 6.23               | 1.03              | 2.73              | 2.47             | 73          | Fair               |\n| 2024-07-19 | 22:09       | 06:07     | 7.54               | 1.57              | 5.25              | 1.03             | 85          | Good               |\n| 2024-07-20 | 02:36       | 07:42     | 4.99               | 1.98              | 2.28              | 0.43             | 64          | Fair               |\n| 2024-07-21 | 22:17       | 07:03     | 8.18               | 1.93              | 4.57              | 2.80             | 87          | Good               |\n| 2024-07-22 | 21:47       | 07:55     | 9.05               | 1.30              | 5.30              | 2.63             | 84          | Good               |\n| 2024-07-23 | 21:51       | 08:01     | 9.00               | 1.57              | 5.00              | 3.20             | 82          | Good               |\n| 2024-07-24 | 22:32       | 05:18     | 6.20               | 1.38              | 4.13              | 0.68             | 74          | Fair               |\n| 2024-07-25 | 21:23       | 05:13     | 7.25               | 1.80              | 4.17              | 1.07             | 78          | Fair               |\n\n#### Key Insights\n- **Sleep Quality**: The overall sleep quality varied from Fair to Good, with the highest score of 87 on July 21.\n- **Deep Sleep**: The percentage of deep sleep was generally good, with the highest deep sleep duration recorded on July 20 (1.98 hours).\n- **REM Sleep**: The REM sleep duration fluctuated, with the highest recorded on July 23 (3.20 hours).\n- **Awake Count**: The number of times you woke up during the night was generally low, with a maximum of 3 awakenings on July 25.\n- **Respiration Rates**: Your average respiration rate remained stable, ranging from 13 to 21 breaths per minute.\n\n#### Recommendations\n1. **Sleep Consistency**: Aim for a more consistent sleep schedule to improve overall sleep quality. Going to bed and waking up at the same time can help regulate your body's internal clock.\n2. **Deep Sleep Enhancement**: Consider incorporating relaxation techniques before bed, such as meditation or gentle stretching, to enhance deep sleep duration.\n3. **Monitor Stress Levels**: Since your sleep stress levels were noted as Fair, finding ways to manage daily stress could positively impact your sleep quality.\n\n### Conclusion\nYour sleep patterns indicate a generally healthy sleep routine, with some fluctuations in quality and duration. By focusing on consistency and stress management, you can further improve your sleep quality. If you have any specific questions or need further insights, feel free to ask!",
          "isUserMessage": false,
          "apiAIModelName": "GPT-4o-mini",
          "dateGenerate": "2024-07-25 14:21",
          "imageLocations": [],
          "aiCharacterName": "dietetist",
          "messageId": 1533
        }
      ],
      "ai_character_name": "dietetist",
      "sessionId": "13893437-7282-4c5f-9955-acbfd13b0177"
    }
  ])
  // need to use useState - because before calling chat api - if we want to add more context with data (from Health) - then we need to wait until data is updated (ahh async react - love you )
  const [triggerAPI, setTriggerAPI] = useState(false);

  // custom hook
  const { callChatAPI } = useChatAPI();

  // if i right click on any message (to show context window) - we need to reset previous context window 
  // if i clicked 2 time on 2 diff messages - two diff context menu were shown
  const [contextMenuIndex, setContextMenuIndex] = useState(null);
  const currentSessionIndex = 0;
  const [isMinimized, setIsMinimized] = useState(true);
  const [previousSize, setPreviousSize] = useState({
    width: isMobile ? 335 : 500, height: isMobile ? 300 : 300
  });

  const handleSendClick = () => {
    setErrorMsg('');
    const modelName = getTextModelName();
    // TODO - change!
    setTextAICharacter('dietetist');

    if (userInput.trim() === '') {
      setErrorMsg("Please provide your input");
      return;
    }

    if (attachedImages.length > 0 && modelName !== 'GPT-4o' && modelName !== 'GPT-4o-mini' && modelName !== 'GPT-4' && modelName !== 'Claude-3.5') {
      setErrorMsg("Currently chosen model does not support images. Remove image or change the model");
      return;
    }

    // if it's first message - attach context (data)
    if (chatContent[currentSessionIndex].messages.length === 0) {
      const fullMessage = data ? `${JSON.stringify(data)}\n${userInput}` : userInput;
      setUserInput(fullMessage);
      if (config.VERBOSE_SUPERB === 1)
        console.log("full health data: ", fullMessage)
    }

    // Set the trigger to call API
    setTriggerAPI(true);
  };

  useEffect(() => {
    if (triggerAPI) {
      if (editingMessage !== null) {
        callChatAPI(editingMessage);
      } else {
        callChatAPI();
      }
      setTriggerAPI(false); // Reset the trigger

      setUserInput("");
      setAttachedImages([]);
      setAttachedFiles([]);
    }
  }, [userInput, triggerAPI, callChatAPI, editingMessage, setUserInput, setAttachedImages, setAttachedFiles]);

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const handleResizeStop = (event, { size }) => {
    setPreviousSize(size);
  };

  return (
    <div className="floating-chat-container">
      {isMinimized ? (
        <button onClick={toggleMinimize} className="floating-chat-minimizedButton">
          <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M120-120v-320h80v184l504-504H520v-80h320v320h-80v-184L256-200h184v80H120Z" /></svg>
        </button>
      ) : (
        <ResizableBox
          width={previousSize.width}
          height={previousSize.height}
          minConstraints={[200, 200]}
          maxConstraints={[window.innerWidth, window.innerHeight]}
          className="floating-chat-resizableBox"
          resizeHandles={['se', 'sw', 'ne', 'nw', 'n', 's', 'e', 'w']}
          onResizeStop={handleResizeStop}
        >
          <div className="floating-chat-box">
            <button onClick={toggleMinimize} className="floating-chat-minimizeButton">
              <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="m136-80-56-56 264-264H160v-80h320v320h-80v-184L136-80Zm344-400v-320h80v184l264-264 56 56-264 264h184v80H480Z" /></svg>
            </button>
            <div className="floating-chat-messages">
              {chatContent[currentSessionIndex] && chatContent[currentSessionIndex].messages ? (
                chatContent[currentSessionIndex].messages.map((message, index) => (
                  <ChatMessage
                    key={index}
                    index={index}
                    message={message}
                    isLastMessage={index === chatContent[currentSessionIndex].messages.length - 1}
                    isUserMessage={message.isUserMessage}
                    contextMenuIndex={contextMenuIndex}
                    setContextMenuIndex={setContextMenuIndex}
                    isFloating={true}
                  />
                ))
              ) : null}
            </div>
            {errorMsg && <div className="bot-error-msg">{errorMsg}</div>}
            <BottomToolsMenu
              handleSendClick={handleSendClick}
              isFloating={true}
            />
          </div>
        </ResizableBox>
      )}
    </div>
  );
};


export default FloatingChat;
