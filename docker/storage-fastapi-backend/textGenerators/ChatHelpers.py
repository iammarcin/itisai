import tiktoken
import logconfig
logger = logconfig.logger

def prepare_chat_history(chat_history, memory_token_limit, model_name):
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