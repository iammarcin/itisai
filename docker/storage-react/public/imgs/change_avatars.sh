
initialComboBoxOptionsPeopleToTalkTo=(
initialComboBoxOptionsStoryRickAndMorty=(
  '{"chat_memory_short_name": "Narrator", "label": "Rick and Morty v1", "avatar": "story_rick1", "welcome_msg": "Random Rick and Morty story, crafted especially for you!", "wait_for_user_input": false }'
  '{"chat_memory_short_name": "Narrator", "label": "Rick and Morty v2", "avatar": "story_rick0", "welcome_msg": "Welcome to Rick and Morty special! Let'"'"'s have our own Rick and Morty episode. What adventure do you want to have?", "wait_for_user_input": true }'
  '{"chat_memory_short_name": "Narrator", "label": "Intergalactic Games", "avatar": "story_rick2", "welcome_msg": "Rick and Morty are invited to a high-stakes intergalactic game show where the contestants are pitted against each other in bizarre challenges. They must outsmart and outperform their competitors to win the grand prize while uncovering the dark secret behind the show.", "voice": "Rick", "wait_for_user_input": false }'
  '{"chat_memory_short_name": "Narrator", "label": "Time flows in reverse", "avatar": "story_rick4", "welcome_msg": "Rick and Morty are transported to a world where time flows in reverse. As they try to adapt to this strange environment, they must unravel the mystery of an impending catastrophe that threatens to erase the entire world from existence and find a way to stop it before it'"'"'s too late.", "voice": "Rick", "wait_for_user_input": false }'
  '{"chat_memory_short_name": "Narrator", "label": "Public thoughts", "avatar": "story_rick5", "welcome_msg": "Rick and Morty find themselves in a dimension where everyone'"'"'s thoughts and inner monologues are visible as floating text above their heads. Rick and Morty must navigate the challenges of total transparency while uncovering a conspiracy to control people'"'"'s thoughts.", "voice": "Rick", "wait_for_user_input": false }'
  '{"chat_memory_short_name": "Narrator", "label": "A.S.I. on Earth", "avatar": "story_rick8", "welcome_msg": "Rick and Morty discover the existence of an A.S.I. (Artificial Superintelligence) on Earth that is more intelligent than any human being. Even Rick!", "voice": "Rick", "wait_for_user_input": false }'
  '{"chat_memory_short_name": "Narrator", "label": "A.S.I. - Galactic Fedaration", "avatar": "story_rick10", "welcome_msg": "A.S.I. (Artificial Superintelligence) takes over the Galactic Federation and plans to control the universe. Rick and Morty must team up with unlikely allies to prevent the A.S.I. from achieving its goal!", "voice": "Rick", "wait_for_user_input": false }'
  '{"chat_memory_short_name": "Narrator", "label": "A.S.I. - Earth conquered", "avatar": "story_rick11", "welcome_msg": "Rick and Morty are transported into an alternate reality where the A.S.I. (Artificial Superintelligence) has already conquered Earth. They must join a human resistance group and use their wits to outsmart the A.S.I. and find a way back to their reality.", "voice": "Rick", "wait_for_user_input":


  '{"chat_memory_short_name": "Narrator", "voice": "Sherlock", "label": "Random story", "avatar": "story_random", "welcome_msg": "Random story especially for you!", "wait_for_user_input": false }'
  '{"chat_memory_short_name": "", "voice": "Sherlock", "label": "Your own story", "avatar": "story_yours", "welcome_msg": "What would you like the story to be about? Choose any topic or provide your description!", "wait_for_user_input": true }'
  '{"chat_memory_short_name": "Narrator", "voice": "Sherlock", "label": "Harry Potter", "avatar": "story_hpotter", "welcome_msg": "Harry Potter and friends find themselves in unexpected situation", "wait_for_user_input": false }'
  '{"chat_memory_short_name": "Narrator", "voice": "Sherlock", "label": "Conscious AI", "avatar": "story_conscious_ai", "welcome_msg": "AI becomes conscious", "wait_for_user_input": false }'
  '{"chat_memory_short_name": "Narrator", "voice": "Sherlock", "label": "Conscious AI v2", "avatar": "story_conscious_ai_v2", "welcome_msg": "AI becomes conscious v2", "wait_for_user_input": false }'
  '{"chat_memory_short_name": "Narrator", "voice": "Sherlock", "label": "AI bot gone rogue", "avatar": "story_ai_gone_rogue", "welcome_msg": "AI bot gone rogue", "wait_for_user_input": false }'
)


for option in "${initialComboBoxOptionsPeopleToTalkTo[@]}"
do
  avatar=$(echo "$option" | jq -r '.avatar')
  value=$(echo "$option" | jq -r '.value')
  mv "$avatar.png" "$value.png"
done
