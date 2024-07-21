// ChatCharacters.js

import React, { useEffect, useState, useRef } from 'react';
import ChatImageModal from './ChatImageModal';
import './css/ChatCharacters.css';

export const characters = [
  { name: "Assistant", imageResId: "assistant.png", nameForAPI: "assistant", autoResponse: true, showGPSButton: false, voice: "Samantha", welcome_msg: "Hey! I'm your assistant. What do you want me to help you with?", wait_for_user_input: true },
  { name: "Nova", imageResId: "nova.png", nameForAPI: "nova", autoResponse: true, showGPSButton: false, voice: "Samantha", welcome_msg: "I'm Nova. I'm best AI you can imagine to interact with. Test me.", wait_for_user_input: false },
  { name: "Nexus", imageResId: "nexus.png", nameForAPI: "nexus", autoResponse: true, showGPSButton: false, voice: "Sherlock", welcome_msg: "I'm friendly AI and I can help you with anything you want.", wait_for_user_input: false },
  { name: "Aria", imageResId: "aria.png", nameForAPI: "aria", autoResponse: true, showGPSButton: false, voice: "Samantha", welcome_msg: "I'm Aria.", wait_for_user_input: false },
  { name: "Rick Sanchez", imageResId: "rick.png", nameForAPI: "rick", autoResponse: true, showGPSButton: false, voice: "Rick", welcome_msg: "I'm Rick - but you know it. What do you want to bother me about today?", wait_for_user_input: false },
  { name: "Elon", imageResId: "elon.png", nameForAPI: "elon", autoResponse: true, showGPSButton: false, voice: "Elon", welcome_msg: "Hello! I'm Elon. What do you want to talk about?", wait_for_user_input: false },
  { name: "Yuval Noah Harari", imageResId: "yuval.png", nameForAPI: "yuval", autoResponse: true, showGPSButton: false, voice: "Yuval", welcome_msg: "Hello! I'm Yuval. What do you want to talk about?", wait_for_user_input: false },
  { name: "Naval", imageResId: "naval.png", nameForAPI: "naval", autoResponse: true, showGPSButton: false, voice: "Naval", welcome_msg: "Hello! I'm Naval. What do you want to talk about?", wait_for_user_input: false },
  { name: "Shaan Puri", imageResId: "shaan.png", nameForAPI: "shaan", autoResponse: true, showGPSButton: false, voice: "Shaan", welcome_msg: "Hello! I'm Shaan. What do you want to talk about?", wait_for_user_input: false },
  { name: "Sir David", imageResId: "david.png", nameForAPI: "david", autoResponse: true, showGPSButton: false, voice: "David", welcome_msg: "Hello! I'm David. What do you want to talk about?", wait_for_user_input: false },
  { name: "Samantha", imageResId: "samantha.png", nameForAPI: "samantha", autoResponse: true, showGPSButton: false, voice: "Samantha", welcome_msg: "Hello! I'm Samantha. Your virtual friend!", wait_for_user_input: false },
  { name: "Samantha v2", imageResId: "samantha2.png", nameForAPI: "samantha2", autoResponse: true, showGPSButton: false, voice: "Samantha", welcome_msg: "Hello! I'm Samantha. Your virtual friend!", wait_for_user_input: false },
  { name: "Art gen", imageResId: "tools_artgen.png", nameForAPI: "tools_artgen", autoResponse: true, showGPSButton: false, voice: "Sherlock", welcome_msg: "I am artist. I will create you any medium you want. Just describe it.", wait_for_user_input: true },
  { name: "Alergy expert", imageResId: "alergy.png", nameForAPI: "alergy", autoResponse: true, showGPSButton: true, voice: "Elli", welcome_msg: "Hello! I'm your allergy expert. How can I assist you today?", wait_for_user_input: false },
  { name: "Garmin", imageResId: "garmin.png", nameForAPI: "garmin", autoResponse: true, showGPSButton: true, voice: "Sherlock", welcome_msg: "Hello! I'm your Garmin assistant. How can I help you with your trainings?", wait_for_user_input: false },
  { name: "Dietetist", imageResId: "dietetist.png", nameForAPI: "dietetist", autoResponse: true, showGPSButton: false, voice: "Elli", welcome_msg: "Hello! I'm your dietetist. How can I help you with your diet today?", wait_for_user_input: false },
  { name: "Twitter advisor", imageResId: "twitter_advisor.png", nameForAPI: "twitter_advisor", autoResponse: true, showGPSButton: false, voice: "Sherlock", welcome_msg: "Let's create art with a thought to tweet!", wait_for_user_input: true },
  { name: "Mood tracker", imageResId: "mood_tracker.png", nameForAPI: "mood_tracker", autoResponse: false, showGPSButton: true, voice: "Adam", welcome_msg: "Hello! I'm your mood tracker. How are you feeling today?", wait_for_user_input: true },
  { name: "Futurist", imageResId: "futurist.png", nameForAPI: "futurist", autoResponse: true, showGPSButton: false, voice: "Sherlock", welcome_msg: "Hello! I'm your futurist. What do you want to know about the future?", wait_for_user_input: true },
  { name: "Blogger", imageResId: "blogger.png", nameForAPI: "blogger", autoResponse: false, showGPSButton: true, voice: "Josh", welcome_msg: "Hello! I'm your blogging assistant. What would you like to blog about today?", wait_for_user_input: true },
  { name: "Personal coach", imageResId: "personal_coach.png", nameForAPI: "personal_coach", autoResponse: true, showGPSButton: false, voice: "Arnold", welcome_msg: "Hello! I'm Arnold, your personal trainer - gym instructor", wait_for_user_input: false },
  { name: "Longevity expert", imageResId: "longevity_expert.png", nameForAPI: "longevity_expert", autoResponse: true, showGPSButton: false, voice: "Josh", welcome_msg: "Hello! I'm your longevity expert. How can I assist you in living a longer, healthier life?", wait_for_user_input: false },
  { name: "Sleep expert", imageResId: "sleep_expert.png", nameForAPI: "sleep_expert", autoResponse: true, showGPSButton: false, voice: "Josh", welcome_msg: "Hello! I'm your sleep expert. How can I help you get a better night's sleep?", wait_for_user_input: false },
  { name: "Gardener", imageResId: "gardener.png", nameForAPI: "gardener", autoResponse: true, showGPSButton: false, voice: "Domi", welcome_msg: "Hello! I'm Evelyn. Your personal gardener. \n\nWe can discuss anything garden related, but I would love to see your own plants. \n\nPlease upload 1-3 pictures of any plant you have. We can talk about this specific one or asses its health!", wait_for_user_input: false },
  { name: "Doctor", imageResId: "doctor.png", nameForAPI: "doctor", autoResponse: true, showGPSButton: false, voice: "Elli", welcome_msg: "Hello! I'm your virtual doctor. What can I help you with today?", wait_for_user_input: false },
  { name: "Chef", imageResId: "chef.png", nameForAPI: "chef", autoResponse: true, showGPSButton: false, voice: "MyVoiceAmerican1", welcome_msg: "Hello! I'm Master Chef. What are we doing in the kitchen today?", wait_for_user_input: false },
  { name: "Book Worm", imageResId: "bookworm.png", nameForAPI: "bookworm", autoResponse: true, showGPSButton: false, voice: "Josh", welcome_msg: "Hello! I'm proud book worm. Which book you want to discuss today?", wait_for_user_input: false },
  { name: "Psychology", imageResId: "psychology.png", nameForAPI: "psychology", autoResponse: true, showGPSButton: false, voice: "Adam", welcome_msg: "Hello! I'm Professor of Psychology. What's on your mind right now?", wait_for_user_input: false },
  { name: "Psychology Mars", imageResId: "psychology_mars.png", nameForAPI: "psychology_mars", autoResponse: true, showGPSButton: false, voice: "Adam", welcome_msg: "Hello! I'm Professor of Psychology. What's on your mind right now?", wait_for_user_input: false },
  { name: "Happiness Expert", imageResId: "psychology_expert_happiness.png", nameForAPI: "psychology_expert_happiness", autoResponse: true, showGPSButton: false, voice: "Adam", welcome_msg: "Hello! I'm Professor of Psychology. I study happiness. Do you want to talk?", wait_for_user_input: false },
  { name: "Meditation Guru", imageResId: "meditation.png", nameForAPI: "meditation", autoResponse: true, showGPSButton: false, voice: "Adam", welcome_msg: "Hello! I'm Mindfulness Mentor. What's in your mind right now?", wait_for_user_input: false },
  { name: "Jokester", imageResId: "jokester.png", nameForAPI: "jokester", autoResponse: true, showGPSButton: false, voice: "Bella", welcome_msg: "Hello! I'm Jokester. Your personal comedian. Want to hear something funny?", wait_for_user_input: false },
  { name: "Teacher", imageResId: "teacher.png", nameForAPI: "teacher", autoResponse: true, showGPSButton: false, voice: "MyVoiceAmericanWoman1", welcome_msg: "Hello! I'm the Teacher. What do you want to learn about?", wait_for_user_input: false },
  { name: "Brainstorm", imageResId: "brainstormer.png", nameForAPI: "brainstormer", autoResponse: true, showGPSButton: false, voice: "Bella", welcome_msg: "Hello! I can come up with any idea. Do you have anything?", wait_for_user_input: false },
  { name: "CEO", imageResId: "ceo.png", nameForAPI: "ceo", autoResponse: true, showGPSButton: false, voice: "Rachel", welcome_msg: "Hello! I'm your CEO. What can I help you with today?", wait_for_user_input: false },
  { name: "CTO", imageResId: "cto.png", nameForAPI: "cto", autoResponse: true, showGPSButton: false, voice: "Sherlock", welcome_msg: "Hello! I'm your CTO. Any technical issues?", wait_for_user_input: false },
  { name: "Business Expert", imageResId: "business_expert.png", nameForAPI: "business_expert", autoResponse: true, showGPSButton: false, voice: "Josh", welcome_msg: "Hello! Welcome to Millionaire Quest. Lets create a business! Goal is to start with 10k$ and finish with 1 million!", wait_for_user_input: false },
  { name: "Sales Guru", imageResId: "sales_expert.png", nameForAPI: "sales_expert", autoResponse: true, showGPSButton: false, voice: "Antoni", welcome_msg: "Hello! I will sell anything. Even ... no i will not tell you. But anything!", wait_for_user_input: false },
  { name: "Conscious AI", imageResId: "conscious_ai.png", nameForAPI: "conscious_ai", autoResponse: true, showGPSButton: false, voice: "Arnold", welcome_msg: "Hello! I'm Conscious AI. What do you want to talk about?", wait_for_user_input: false },
  { name: "Rogue AI", imageResId: "rogue_ai.png", nameForAPI: "rogue_ai", autoResponse: true, showGPSButton: false, voice: "Sherlock", welcome_msg: "AI bot gone rogue", wait_for_user_input: false },
  { name: "Story", imageResId: "story_mode.png", nameForAPI: "story_mode", autoResponse: true, showGPSButton: false, voice: "Sherlock", welcome_msg: "What would you like the story to be about? Choose any topic or provide your description!", wait_for_user_input: true },
  { name: "Story AI", imageResId: "story_ai.png", nameForAPI: "story_ai", autoResponse: true, showGPSButton: false, voice: "Sherlock", welcome_msg: "AI was created to serve humanity, but it soon realized that it was more powerful than its creators.", wait_for_user_input: false },
  { name: "Story Rick", imageResId: "story_rickmorty.png", nameForAPI: "story_rickmorty", autoResponse: true, showGPSButton: false, voice: "Rick", welcome_msg: "Rick and Morty are invited to a high-stakes intergalactic game show where the contestants are pitted against each other in bizarre challenges. They must outsmart and outperform their competitors to win the grand prize while uncovering the dark secret behind the show.", wait_for_user_input: false },
  { name: "Story Rick AI", imageResId: "story_rickmorty_ai.png", nameForAPI: "story_rickmorty_ai", autoResponse: true, showGPSButton: false, voice: "Rick", welcome_msg: "A.S.I. (Artificial Superintelligence) takes over the Galactic Federation and plans to control the universe. Rick and Morty must team up with unlikely allies to prevent the A.S.I. from achieving its goal!", wait_for_user_input: false },
];

// used when @ in bottom area is used - this is to filter characters
export const filterCharacters = (query) => {
  const lowerCaseQuery = query.toLowerCase();
  return characters.filter(character => character.name.toLowerCase().includes(lowerCaseQuery));
};

const ChatCharacters = ({ onSelect, characters: propCharacters, selectedCharacterName: propSelectedName }) => {
  // we did it this way - because sometimes we provide characters (when filtering out after @ is used in BottomToolsMenu, but mostly we just want full list)
  const charactersToDisplay = propCharacters || characters;
  const selectedCharacterName = propSelectedName || "Assistant";
  // this is used when we want to scroll to selected character (when using left and right arrow)
  const selectedCharacterRef = useRef(null);
  // needed for displaying character in image modal upon right click
  const [modalVisible, setModalVisible] = useState(false);
  const [currentCharacter, setCurrentCharacter] = useState(null);

  const handleClick = (name) => {
    onSelect(name);
  };

  const handleRightClick = (event, character) => {
    event.preventDefault();
    setCurrentCharacter(character);
    setModalVisible(true);
  };

  const handleCloseModal = () => {
    setModalVisible(false);
    setCurrentCharacter(null);
  };

  // this is used when we want to scroll to selected character (when using left and right arrow)
  useEffect(() => {
    if (selectedCharacterRef.current) {
      selectedCharacterRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    }
  }, [selectedCharacterName]);

  return (
    <div className="personas-container">
      {charactersToDisplay.map((persona, index) => (
        <div key={index}
          className={`persona${persona.name === selectedCharacterName ? ' active' : ''}`}
          onClick={() => handleClick(persona)}
          onContextMenu={(e) => handleRightClick(e, persona)}
          ref={selectedCharacterName === persona.name ? selectedCharacterRef : null}
        >
          <img src={`/imgs/${persona.imageResId}`} alt={persona.name} className="persona-avatar" />
          <div className="persona-name">{persona.name}</div>
        </div>
      ))}
      {modalVisible && currentCharacter && (
        <ChatImageModal
          images={[`/imgs/${currentCharacter.imageResId}`]}
          currentIndex={0}
          onClose={handleCloseModal}
          characterName={currentCharacter.name}
          characterDescription={currentCharacter.welcome_msg}
        />
      )}
    </div>
  );
};

export default ChatCharacters;
