import tiktoken
import logconfig
logger = logconfig.logger

# prepare chat history to be sure that we fit into memory limit defined by user
def prepare_chat_history(chat_history, memory_token_limit, model_name):
  total_tokens = 0
  trimmed_messages = []

  for message in reversed(chat_history):
    message_tokens = num_tokens_from_string(message["content"], model=model_name)
    if total_tokens + message_tokens > memory_token_limit:
      # If adding this message exceeds the limit, trim the message content
      remaining_tokens = memory_token_limit - total_tokens

      # Approximate trimming by percentage
      # this is bit dirty trick - but idea was that i want to trim first part of the message (to have continuity in chat)
      # and we would need to encode and decode exactly message to get it precisely
      # so i dediced that more or less is enough - and i will just cut % of the message (knowing how many tokens i have to trim to fit into limit)
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