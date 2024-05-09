import tiktoken
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from prompts.text import getTextPromptTemplate
import random
import logconfig
logger = logconfig.logger

def prepareFinalPromptForChat(userInput: dict, assetInput: dict, memory_token_limit: int, prompt_total_limit: int, model_name: str):
    whoIsTalking = userInput.get('whoIsTalking') if userInput.get('whoIsTalking') != None else "AI"
    userMessage = userInput.get('userMessage')

    switchCategory = userInput.get('switchCategory')
    logger.info("!"*100)
    logger.info("userInput: %s" % userInput)

    # set chat mode properly... if someone provided chat mode than that's clear
    # if not provided at all - lets fall back to chat
    # if provided but history mode or brainstorm mode
    # it means that user didnt choose subchoice (who does he want to talk to or what is topic of story)
    # so he provided himself name or topic of story
    chatSelectUserMainChoice = userInput.get('chatSelectUserMainChoice')
    chatSelectUserCustomChoice = userInput.get('chatSelectUserCustomChoice')
    # specific info to adjust the prompt (for example if gardener mode is used - we might use different kind of prompts - analysis, identify etc)
    # its either number - prompt mode - or additional text - context info
    additionalPromptContextInfo = userInput.get('additionalPromptContextInfo')
    additionalPromptMode = userInput.get('additionalPromptMode')
    # this is needed to fill name in memory (to set properly the converstation)
    if chatSelectUserMainChoice == "storyMode" or chatSelectUserMainChoice == "brainstormMode" or chatSelectUserMainChoice == "rickmortyMode":
      whoIsTalking = chatSelectUserCustomChoice

    chat_mode = chatSelectUserMainChoice if chatSelectUserMainChoice != None else "chat"

    logger.info("!!!"*30)
    logger.info("chatSelectUserMainChoice: %s" % chatSelectUserMainChoice)
    logger.info("chatSelectUserCustomChoice: %s" % chatSelectUserCustomChoice)
    logger.info("chat_mode: %s" % chat_mode)
    # those are cases from text2youtube
    if chatSelectUserMainChoice == "video_text" and switchCategory != "":
        if switchCategory == "Random":
          # come up with random number between 1 and 3
          # and use it to select one of the modes - video_text_random{number}
          random_number = random.randint(1, 2)
          chat_mode = "video_text_random" + str(random_number)
        elif switchCategory == "Teach me":
          chat_mode = "video_text_teach_me"
        elif switchCategory == "Story":
          chat_mode = "video_text_story"
        else:
          chat_mode = chatSelectUserMainChoice

    # here we add potential modifier to chat_mode name - so for example brainstormGardener - becomes brainstormGardener_1
    chat_mode = chat_mode + "_" + str(additionalPromptMode) if additionalPromptMode != 0 else chat_mode

    template = getTextPromptTemplate(chat_mode)['template']
    logger.info("template: %s" % template)

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    logger.debug("system_message_prompt: %s" % system_message_prompt)
    if chatSelectUserMainChoice == "storyMode" or chatSelectUserMainChoice == "rickmortyMode" or chatSelectUserMainChoice == "toolsMode":
      human_template="{text} \n\n"
    elif chatSelectUserMainChoice == "videoMode" or chatSelectUserMainChoice == "text2image_prompt" or chatSelectUserMainChoice == "video_text":
      human_template="\n\n"
    #elif chatSelectUserMainChoice == "brainstormGardener" and additionalPromptMode == True:
    #  human_template="You've just identified this plant. Please explain it.\n\nEvelyn: "
    else:
      human_template="{text} \n\n" + str(whoIsTalking) + ": "
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    # final template
    chat_prompt_template = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

    messageHistory = assetInput[0]['messages']

    memory_for_prompt = format_memory_for_final_prompt(template, messageHistory, whoIsTalking, memory_token_limit, prompt_total_limit, model_name)

    # prompt template to text
    # for main methods (without specific choice) we need to add additionally chatSelectUserCustomChoice
    if chatSelectUserMainChoice == "storyMode" or chatSelectUserMainChoice == "rickmortyMode" or chatSelectUserMainChoice == "brainstormMode" or chatSelectUserMainChoice == "artistMode":
      final_prompt = chat_prompt_template.format_prompt(history=memory_for_prompt, text=userMessage, chatSelectUserCustomChoice=chatSelectUserCustomChoice).to_messages()
    elif chatSelectUserMainChoice == "videoMode":
      final_prompt = chat_prompt_template.format_prompt().to_messages()
    elif additionalPromptContextInfo != None: # if additional context in use - lets add it to prompts
      final_prompt = chat_prompt_template.format_prompt(history=memory_for_prompt, text=userMessage, additionalPromptContextInfo=additionalPromptContextInfo).to_messages()
    #elif chatSelectUserMainChoice == "brainstormGardener":
    #  if additionalPromptMode == True:
    #    system_message_prompt = SystemMessagePromptTemplate.from_template("brainstormGardenerFirstPromptAfterIdentify")
    #  # special case for gardener - as we're adding context of plant (or not if its not identified)
    #  final_prompt = chat_prompt_template.format_prompt(history=memory_for_prompt, text=userMessage, additionalPromptContextInfo=additionalPromptContextInfo).to_messages()
    else:
      final_prompt = chat_prompt_template.format_prompt(history=memory_for_prompt, text=userMessage).to_messages()
    logger.info("!_"*100)
    logger.info("memory_for_prompt: %s" % memory_for_prompt)
    logger.info("final_prompt: %s" % final_prompt)
    logger.info(userInput.get('type'))

    return final_prompt

def format_memory_for_final_prompt(template, memory, whoIsTalking, max_limit, hard_limit, model):
    memory_prompt = ''
    memory_len = 0
    #logger.info("message['persona'] %s" % message['persona'])
    for message in reversed(memory):
        content = message['data']['content']
        content_type = message['type']
        if content_type == 'ai':
            persona = message['persona'] or "ai"
            # if persona starts with brainstorm
            # lets remove it from persona
            if persona.startswith("brainstorm") or persona.startswith("toolsMode"):
              persona = persona.replace("brainstorm", "").replace("toolsMode", "")
            else:
              persona = whoIsTalking
            content_type = persona
        elif content_type == 'human':
            content_type = 'Human'
        formatted_message = f"{content_type}: {content}\n"

        remaining_space = max_limit - memory_len
        formatted_message_tokens = num_tokens_from_string(formatted_message, model)
        if formatted_message_tokens > remaining_space:
            start_index = formatted_message_tokens - remaining_space
            formatted_message = formatted_message[start_index:]

        memory_prompt = formatted_message + memory_prompt
        memory_len += formatted_message_tokens

        if memory_len >= max_limit:
            break

    full_prompt = template.strip() + "\n" + memory_prompt
    full_prompt_tokens = num_tokens_from_string(full_prompt, model)
    if full_prompt_tokens > hard_limit:
        excess_chars = full_prompt_tokens - hard_limit
        memory_prompt = memory_prompt[excess_chars:]

    return memory_prompt

def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens