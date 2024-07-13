import tiktoken
import requests
import mimetypes
import base64
import copy
import json
import asyncio

import pypdfium2 as pdfium
from PIL import Image
from aws.awsProvider import awsProvider

from pathlib import Path
from tempfile import NamedTemporaryFile

import config as config
import logconfig
logger = logconfig.logger

# little helper class - s3 upload in aws provider was already set and used by other functions
# and it needs file and filename to process the file
class FileWithFilename:
    def __init__(self, file, filename):
        self.file = file
        self.filename = filename

# file_attached_message_limit - how many user messages can be sent before we start trimming image or files URLs / base64
# goal is to feed openai API with file/image URLs only when necessary (for few messages, later for sure topic will change)
# support_image_input some model support images (and files - because in the end pdfs are for files) as input, some not
def prepare_chat_history(chat_history, memory_token_limit, model_name, support_image_input, use_base64=True, file_attached_message_limit=3):
    total_tokens = 0
    trimmed_messages = []
    user_message_count = 0
    # this it to rack role for messages - to make sure that there is alternate order (user , assistant) always. other way - Claude will not proceed
    last_role = None

    for message in reversed(chat_history):
        message_tokens = 0
        message_content = ""

        # Check if the message has a content list
        # this should be message - with text and potentially additional images etc - this should be standard
        if isinstance(message["content"], list):
            # sometimes message can empty and then it looks like :
            # {'role': 'user', 'content': [{'type': 'text', 'text': ''}]}
            # in this case we should skip it
            if message.get('content')[0].get('text') == "":
                continue

            if message["role"] == "user":
                # increase counter - so we know when to stop using images
                user_message_count += 1

            # if previous message was also from same role (user or assistant) - then lets skip it - because Claude will fail. and most probably this is error
            if last_role == message["role"] and isItAnthropicModel(model_name):
                continue

            last_role = message["role"]

            text_content = next((item["text"] for item in message['content'] if item["type"] == "text"), "")
            image_urls = [item["image_url"]['url'] for item in message['content'] if item["type"] == "image_url"]
            file_urls = [item["file_url"]['url'] for item in message['content'] if item["type"] == "file_url"]

            message_tokens = num_tokens_from_string(text_content, model=model_name)

            # check if we should use images / files in API request
            if support_image_input and (image_urls or file_urls) and file_attached_message_limit > user_message_count:
                message_content = prepare_message_content(message['content'], model_name, use_base64).get('content')
            else:
                message_content = text_content

        else:
            # Handle simple text messages
            message_content = message["content"]
            message_tokens = num_tokens_from_string(message_content, model=model_name)

        # Check if adding this message exceeds the limit
        if total_tokens + message_tokens > memory_token_limit:
            remaining_tokens = memory_token_limit - total_tokens

            # Approximate trimming by percentage
            # this is bit dirty trick - but idea was that i want to trim first part of the message (to have continuity in chat)
            # and we would need to encode and decode exactly message to get it precisely
            # so i decided that more or less is enough - and i will just cut % of the message (knowing how many tokens i have to trim to fit into limit)
            if message_tokens > 0:  # Avoid division by zero
                trim_percentage = (message_tokens - remaining_tokens) / message_tokens
                # for simple messages
                if isinstance(message_content, str):
                    trim_index = int(len(message_content) * (trim_percentage))
                    message_content = message_content[trim_index:]
                # for those more complex with content
                elif isinstance(message_content, list):
                    text_item = next(item for item in message_content if item["type"] == "text")
                    trim_index = int(len(text_item["text"]) * (trim_percentage))
                    text_item["text"] = text_item["text"][trim_index:]

        trimmed_messages.insert(0, {"role": message["role"], "content": message_content})
        total_tokens += message_tokens

        if total_tokens >= memory_token_limit:
            break

    # Ensure the conversation starts with a user message for Anthropic models
    if isItAnthropicModel(model_name):
        if trimmed_messages and trimmed_messages[0]["role"] != "user":
            # cannot be totally empty
            trimmed_messages.insert(0, {"role": "user", "content": "."})

    return trimmed_messages

def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    if isItAnthropicModel(model):
        # not accurate - but according to Anthropic docs "a token approximately represents 3.5 English characters"
        num_tokens = len(string) / 3.5
        return int(num_tokens)

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = len(encoding.encode(string))
    return num_tokens

# as it is used in multiple places - i created function
# this is to identify if model is from Anthropic / Claude
def isItAnthropicModel(model_name: str) -> bool:
    model_name = model_name.lower()
    if model_name.startswith("claude") or model_name.startswith("anthropic"):
        return True
    else:
        return False

# IMAGE PART
def download_file(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    return response

def get_mime_type(image_content):
    mime_type, _ = mimetypes.guess_type(image_content)
    return mime_type

def calculate_base64(image_content):
    return base64.b64encode(image_content).decode('utf-8')

def get_base64_for_image(url):
    image_content = download_file(url)

    mime_type = get_mime_type(url)
    print(f"MIME type: {mime_type}")
    base64_encoding = calculate_base64(image_content.content)

    return mime_type, base64_encoding

def prepare_image_content(image_urls, model_name, use_base64):
    image_content = []

    for url in image_urls:
        if isItAnthropicModel(model_name):
            use_base64 = True
            mime_type, base64_encoding = get_base64_for_image(url)
            image_content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": base64_encoding,
                },
            })
        else:
            if use_base64:
                mime_type, base64_encoding = get_base64_for_image(url)
                image_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_encoding}",
                    },
                })
            else:
                image_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": url,
                    },
                })
    return image_content

# within chat_history or for user message we need to process it - because there are differences between generators - especially if there are images
def prepare_message_content(message, model, use_base64):
    # Handle messages with multiple content types (text and images)
    text_content = next((item["text"] for item in message if item["type"] == "text"), "")
    image_urls = [item["image_url"]['url'] for item in message if item["type"] == "image_url"]
    file_urls = [item["file_url"]['url'] for item in message if item["type"] == "file_url"]
    print("FILE URLS:   ", file_urls)
    # Filter out empty strings and check if the resulting list is not empty
    valid_file_urls = [url for url in file_urls if url.strip()]
    if valid_file_urls:
        response_files = process_attached_files(file_urls)
        for file in response_files:
            # add file to image_urls
            image_urls.append(file)

    image_content = prepare_image_content(image_urls, model, use_base64)

    message_content = {
        "role": "user",
        "content": [{"type": "text", "text": text_content}] + image_content,
    }

    return message_content

def process_attached_files(file_urls):
    logger.debug("File urls: %s", file_urls)
    final_urls = []
    for file in file_urls:
        # if its pdf file
        if file.endswith(".pdf"):
            response = download_file(file)
            pdf = pdfium.PdfDocument(response.content)
            for i, page in enumerate(pdf):
                bitmap = page.render(scale=1, rotation=0)
                pil_image = bitmap.to_pil()
                with NamedTemporaryFile(delete=False, suffix=f"_p{i}.png") as tmp_file:
                    tmp_file_path = tmp_file.name
                    pil_image.save(tmp_file, format='PNG')

                with open(tmp_file_path, "rb") as tmp_file:
                    file_with_filename = FileWithFilename(
                        tmp_file, Path(tmp_file_path).name)
                    s3_url = asyncio.run(async_s3_upload(file_with_filename))
                    final_urls.append(s3_url)

    logger.debug("Final URLs: %s", final_urls)
    return final_urls

async def async_s3_upload(file_with_filename):
    s3_response = await awsProvider.s3_upload(
        awsProvider,
        action="s3_upload",
        userInput={"file": file_with_filename},
        assetInput={},
        customerId=1
    )

    s3_response_content = json.loads(s3_response.body.decode("utf-8"))
    s3_url = s3_response_content["message"]["result"]
    return s3_url

# it's bit dumb - but i don't see any other option
# when displaying history and when base64 is in use
# debugging is impossible - because it logs all those loooooong strings for base64
# so this is to avoid it
def truncate_image_urls_from_history(chat_history, max_length=50):
    truncated_history = []

    for entry in chat_history:
        new_entry = copy.deepcopy(entry)
        if 'content' in new_entry:
            if isinstance(new_entry['content'], list):
                new_content = []
                for content_item in new_entry['content']:
                    if isinstance(content_item, dict):
                        new_content_item = content_item.copy()
                        if content_item['type'] == 'image_url' and len(content_item['image_url']['url']) > max_length:
                            new_content_item['image_url']['url'] = content_item['image_url']['url'][:max_length] + '...'
                        # for claude
                        if content_item['type'] == 'image' and len(content_item['source']['data']) > max_length:
                            new_content_item['source']['data'] = content_item['source']['data'][:max_length] + '...'
                        new_content.append(new_content_item)
                    else:
                        new_content.append(content_item)
                new_entry['content'] = new_content
        truncated_history.append(new_entry)

    return truncated_history
