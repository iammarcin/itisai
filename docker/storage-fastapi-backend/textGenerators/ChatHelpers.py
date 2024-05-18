import tiktoken
import logconfig
logger = logconfig.logger


def prepare_chat_history(chat_history, memory_token_limit, model_name):
  total_tokens = 0
  trimmed_messages = []

  logger.info("--------------" * 3)
  for message in reversed(chat_history):
    logger.info("message: %s" % message)
    message_tokens = num_tokens_from_string(message["content"], model=model_name)
    logger.info("message_tokens: %s" % message_tokens)
    if total_tokens + message_tokens > memory_token_limit:
      # If adding this message exceeds the limit, trim the message content
      remaining_tokens = memory_token_limit - total_tokens
      encoding = tiktoken.encoding_for_model(model_name)
      logger.info("encoding: %s" % encoding)
      encoded_message = encoding.encode(message["content"])
      logger.info("encoded_message: %s" % encoded_message)
      trimmed_content = encoding.decode(encoded_message[-remaining_tokens:])  # Take the last part of the message
      logger.info("trimmed_content: %s" % trimmed_content)
      message["content"] = trimmed_content
      trimmed_messages.insert(0, message)
      break
    else:
      total_tokens += message_tokens
      trimmed_messages.insert(0, message)

  return trimmed_messages

def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))
    return num_tokens