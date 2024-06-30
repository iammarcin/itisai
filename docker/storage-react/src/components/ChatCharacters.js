// ChatCharacters.js

import React from 'react';
import './css/ChatCharacters.css'; // Make sure to create appropriate styles

export const characters = [
  { name: "Assistant", imageResId: "assistant.png", nameForAPI: "assistant", autoResponse: true, showGPSButton: false },
  { name: "Art gen", imageResId: "tools_artgen.png", nameForAPI: "tools_artgen", autoResponse: true, showGPSButton: false },
  { name: "Alergy expert", imageResId: "alergy.png", nameForAPI: "alergy", autoResponse: true, showGPSButton: true },
  { name: "Garmin", imageResId: "garmin.png", nameForAPI: "garmin", autoResponse: true, showGPSButton: true },
  { name: "Dietetist", imageResId: "dietetist.png", nameForAPI: "dietetist", autoResponse: true, showGPSButton: false },
  { name: "Blogger", imageResId: "blogger.png", nameForAPI: "blogger", autoResponse: false, showGPSButton: true },
  { name: "Personal coach", imageResId: "personal_coach.png", nameForAPI: "personal_coach", autoResponse: true, showGPSButton: false },
  { name: "Longevity expert", imageResId: "longevity_expert.png", nameForAPI: "longevity_expert", autoResponse: true, showGPSButton: false },
  { name: "Sleep expert", imageResId: "sleep_expert.png", nameForAPI: "sleep_expert", autoResponse: true, showGPSButton: false },
  { name: "Gardener", imageResId: "gardener.png", nameForAPI: "gardener", autoResponse: true, showGPSButton: false },
  { name: "Doctor", imageResId: "doctor.png", nameForAPI: "doctor", autoResponse: true, showGPSButton: false },
  { name: "Chef", imageResId: "chef.png", nameForAPI: "chef", autoResponse: true, showGPSButton: false },
  { name: "Book Worm", imageResId: "bookworm.png", nameForAPI: "bookworm", autoResponse: true, showGPSButton: false },
  { name: "Psychology", imageResId: "psychology.png", nameForAPI: "psychology", autoResponse: true, showGPSButton: false },
  { name: "Psychology Mars", imageResId: "psychology_mars.png", nameForAPI: "psychology_mars", autoResponse: true, showGPSButton: false },
  { name: "Happiness Expert", imageResId: "psychology_expert_happiness.png", nameForAPI: "psychology_expert_happiness", autoResponse: true, showGPSButton: false },
  { name: "Meditation Guru", imageResId: "meditation.png", nameForAPI: "meditation", autoResponse: true, showGPSButton: false },
  { name: "Jokester", imageResId: "jokester.png", nameForAPI: "jokester", autoResponse: true, showGPSButton: false },
  { name: "Teacher", imageResId: "teacher.png", nameForAPI: "teacher", autoResponse: true, showGPSButton: false },
  { name: "Brainstorm", imageResId: "brainstormer.png", nameForAPI: "brainstormer", autoResponse: true, showGPSButton: false },
  { name: "CEO", imageResId: "ceo.png", nameForAPI: "ceo", autoResponse: true, showGPSButton: false },
  { name: "CTO", imageResId: "cto.png", nameForAPI: "cto", autoResponse: true, showGPSButton: false },
  { name: "Business Expert", imageResId: "business_expert.png", nameForAPI: "business_expert", autoResponse: true, showGPSButton: false },
  { name: "Sales Guru", imageResId: "sales_expert.png", nameForAPI: "sales_expert", autoResponse: true, showGPSButton: false },
  { name: "Conscious AI", imageResId: "conscious_ai.png", nameForAPI: "conscious_ai", autoResponse: true, showGPSButton: false },
  { name: "Rogue AI", imageResId: "rogue_ai.png", nameForAPI: "rogue_ai", autoResponse: true, showGPSButton: false },
  { name: "Story", imageResId: "story_mode.png", nameForAPI: "story_mode", autoResponse: true, showGPSButton: false },
  { name: "Story AI", imageResId: "story_ai.png", nameForAPI: "story_ai", autoResponse: true, showGPSButton: false },
  { name: "Story Rick", imageResId: "story_rickmorty.png", nameForAPI: "story_rickmorty", autoResponse: true, showGPSButton: false },
  { name: "Story Rick AI", imageResId: "story_rickmorty_ai.png", nameForAPI: "story_rickmorty_ai", autoResponse: true, showGPSButton: false },
  { name: "Samantha", imageResId: "samantha.png", nameForAPI: "samantha", autoResponse: true, showGPSButton: false },
  { name: "Samantha v2", imageResId: "samantha2.png", nameForAPI: "samantha2", autoResponse: true, showGPSButton: false },
  { name: "Elon", imageResId: "elon.png", nameForAPI: "elon", autoResponse: true, showGPSButton: false },
  { name: "Yuval Noah Harari", imageResId: "yuval.png", nameForAPI: "yuval", autoResponse: true, showGPSButton: false },
  { name: "Naval", imageResId: "naval.png", nameForAPI: "naval", autoResponse: true, showGPSButton: false },
  { name: "Shaan Puri", imageResId: "shaan.png", nameForAPI: "shaan", autoResponse: true, showGPSButton: false },
  { name: "Sir David", imageResId: "david.png", nameForAPI: "david", autoResponse: true, showGPSButton: false },
  { name: "Rick Sanchez", imageResId: "rick.png", nameForAPI: "rick", autoResponse: true, showGPSButton: false },
];

const ChatCharacters = ({ onSelect }) => {

  const handleClick = (name) => {
    onSelect(name);
  };

  return (
    <>

      <div className="personas-container">
        {characters.map((persona, index) => (
          <div key={index} className="persona" onClick={() => handleClick(persona)}>
            <img src={`./imgs/${persona.imageResId}`} alt={persona.name} className="persona-avatar" />
            <div className="persona-name">{persona.name}</div>
          </div>
        ))}
      </div>
    </>
  );
};

export default ChatCharacters;
