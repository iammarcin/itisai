import tiktoken
import logconfig
logger = logconfig.logger

# image_message_limit - how many user messages can be sent after an image message before we start trimming image URLs
# goal is to feed openai API with image URLs only when necessary (for few messages, later for sure topic will change)
def prepare_chat_history(chat_history, memory_token_limit, model_name, image_message_limit=3):
    total_tokens = 0
    trimmed_messages = []
    user_message_count_after_last_image = 0

    for message in reversed(chat_history):
        if isinstance(message["content"], list):
            message_tokens = 0
            text_content_index = None
            include_image_urls = True

            # Calculate the number of tokens for the text part of the message
            for i, content_item in enumerate(message["content"]):
                if content_item["type"] == "text":
                    message_tokens = num_tokens_from_string(content_item["text"], model=model_name)
                    text_content_index = i
                    break

            # Check if we should include image URLs based on the limit
            if any(content_item["type"] == "image_url" for content_item in message["content"]):
                if user_message_count_after_last_image >= image_message_limit:
                    include_image_urls = False
                else:
                    user_message_count_after_last_image = 0

            # Increment the count of user messages after the last image URL
            user_message_count_after_last_image += 1

            # Check if adding this message exceeds the limit
            if total_tokens + message_tokens > memory_token_limit:
                remaining_tokens = memory_token_limit - total_tokens

                if message_tokens > 0:  # Avoid division by zero
                    trim_percentage = (message_tokens - remaining_tokens) / message_tokens
                    trim_index = int(len(message["content"][text_content_index]["text"]) * trim_percentage)
                    message["content"][text_content_index]["text"] = message["content"][text_content_index]["text"][trim_index:]

                if include_image_urls:
                    trimmed_messages.insert(0, message)
                else:
                    message["content"] = [content_item for content_item in message["content"] if content_item["type"] != "image_url"]
                    trimmed_messages.insert(0, message)
                break
            else:
                total_tokens += message_tokens
                if include_image_urls:
                    trimmed_messages.insert(0, message)
                else:
                    message["content"] = [content_item for content_item in message["content"] if content_item["type"] != "image_url"]
                    trimmed_messages.insert(0, message)
        else:
            # For assistant messages which are not lists
            message_tokens = num_tokens_from_string(message["content"], model=model_name)

            if total_tokens + message_tokens > memory_token_limit:
                remaining_tokens = memory_token_limit - total_tokens

                if message_tokens > 0:  # Avoid division by zero
                    trim_percentage = (message_tokens - remaining_tokens) / message_tokens
                    trim_index = int(len(message["content"]) * trim_percentage)
                    message["content"] = message["content"][trim_index:]

                trimmed_messages.insert(0, message)
                break
            else:
                total_tokens += message_tokens
                trimmed_messages.insert(0, message)

    return trimmed_messages

def prepare_chat_historyOLD(chat_history, memory_token_limit, model_name):
    total_tokens = 0
    trimmed_messages = []

    for message in reversed(chat_history):
        # Check if the message has a content list
        # this should be user message - with text and potentially additional images etc
        if isinstance(message["content"], list):
            message_tokens = 0
            text_content_index = None

            # Calculate the number of tokens for the text part of the message
            for i, content_item in enumerate(message["content"]):
                if content_item["type"] == "text":
                    message_tokens = num_tokens_from_string(content_item["text"], model=model_name)
                    text_content_index = i
                    break

            # Check if adding this message exceeds the limit
            if total_tokens + message_tokens > memory_token_limit:
                remaining_tokens = memory_token_limit - total_tokens

                # Approximate trimming by percentage
                # this is bit dirty trick - but idea was that i want to trim first part of the message (to have continuity in chat)
                # and we would need to encode and decode exactly message to get it precisely
                # so i dediced that more or less is enough - and i will just cut % of the message (knowing how many tokens i have to trim to fit into limit)
                if message_tokens > 0:  # Avoid division by zero
                    trim_percentage = (message_tokens - remaining_tokens) / message_tokens
                    trim_index = int(len(message["content"][text_content_index]["text"]) * trim_percentage)
                    message["content"][text_content_index]["text"] = message["content"][text_content_index]["text"][trim_index:]

                trimmed_messages.insert(0, message)
                break
            else:
                total_tokens += message_tokens
                trimmed_messages.insert(0, message)
        else:
            # For assistant messages which are not lists
            message_tokens = num_tokens_from_string(message["content"], model=model_name)

            if total_tokens + message_tokens > memory_token_limit:
                remaining_tokens = memory_token_limit - total_tokens

                # trick with percentage - described above
                if message_tokens > 0:  # Avoid division by zero
                    trim_percentage = (message_tokens - remaining_tokens) / message_tokens
                    trim_index = int(len(message["content"]) * trim_percentage)
                    message["content"] = message["content"][trim_index:]

                trimmed_messages.insert(0, message)
                break
            else:
                total_tokens += message_tokens
                trimmed_messages.insert(0, message)

    return trimmed_messages

def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    try:
      encoding = tiktoken.encoding_for_model(model)
    except KeyError:
      print("Warning: model not found. Using cl100k_base encoding.")
      encoding = tiktoken.get_encoding("cl100k_base")
  
    num_tokens = len(encoding.encode(string))
    return num_tokens