import tiktoken
import requests
import mimetypes
import base64
import copy
import json
import csv
import io
# import asyncio

import pypdfium2 as pdfium
# from PIL import Image
from aws.awsProvider import awsProvider

# from pathlib import Path
from tempfile import NamedTemporaryFile

import config as config
import logconfig
logger = logconfig.logger

DEBUG = config.defaults["DEBUG"]
VERBOSE_SUPERB = config.defaults["VERBOSE_SUPERB"]

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
    # this it to track role for messages - to make sure that there is alternate order (user , assistant) always. other way - Claude will not proceed
    last_role = None
    # this is to track last message - because there were cases where last_role was the same, but last message was empty (because it was recording from android) - so then we don't want to skip current message
    last_message = ""

    # we go from newest to oldest - because if we need to cut of course we will cut older messages
    for message in reversed(chat_history):
        message_tokens = 0
        message_content = ""

        if VERBOSE_SUPERB:
            logger.info("-----")
            logger.info("last_role %s" % last_role)
            logger.info("last_message %s" % last_message)
            logger.info("current message: %s" % message)

        # if previous message was also from same role (user or assistant) - then lets skip it - because Claude will fail. and most probably this is error
        # added later - but (as mentioned above) sometimes last message from same user can be empty - so then we dont want to skip
        if last_role == message["role"] and last_message != "" and isItAnthropicModel(model_name):
            continue

        last_role = message["role"]

        # Check if the message has a content list
        # this should be message - with text and potentially additional images etc - this should be standard user request
        # because usually we provide whole structure in case there are files (images etc) attached
        # if there's no content - probably it might be AI response or some exceptional user message
        if isinstance(message["content"], list):
            last_message = message["content"][0].get('text')
            # sometimes message can empty and then it looks like :
            # {'role': 'user', 'content': [{'type': 'text', 'text': ''}]}
            # in this case we should skip it
            if last_message == "":
                continue

            if message["role"] == "user":
                # increase counter - so we know when to stop using images
                user_message_count += 1

            # we collect text and files (images etc). file_urls - most probably will be pdf if something. audio might be there as well but we won't use them here (as of now)
            text_content = next((item["text"] for item in message['content'] if item["type"] == "text"), "")
            image_urls = [item["image_url"]['url'] for item in message['content'] if item["type"] == "image_url"]
            file_urls = [item["file_url"]['url'] for item in message['content'] if item["type"] == "file_url"]

            # calculate how many tokens we use for this text
            message_tokens = num_tokens_from_string(text_content, model=model_name)

            # check if we should use images / files in API request
            if support_image_input and (image_urls or file_urls) and file_attached_message_limit > user_message_count:
                message_content = prepare_message_content(message['content'], model_name, use_base64).get('content')
            else:
                message_content = text_content

        else:
            # Handle simple text messages (AI response mostly)
            last_message = message["content"]
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
                # for simple messages like AI response
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
    if url.startswith("http"):
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response
    else:
        return url

def get_mime_type(image_content):
    mime_type, _ = mimetypes.guess_type(image_content)
    return mime_type

def calculate_base64(image_content):
    return base64.b64encode(image_content).decode('utf-8')

def get_base64_for_image(url):
    image_content = download_file(url)

    mime_type = get_mime_type(url)
    print(f"MIME type: {mime_type}")
    if url.startswith("http"):
        base64_encoding = calculate_base64(image_content.content)
    else:
        with open(image_content, "rb") as tmp_file:
            base64_encoding = calculate_base64(tmp_file.read())

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

# process attached files - for the moment only supports pdf
# if pdf - transform it to images which later be sent to API
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

                logger.info("tmp_file: %s", tmp_file_path)

                final_urls.append(tmp_file_path)

    logger.debug("Final URLs: %s", final_urls)
    return final_urls

# if asset input is attached (for example in Health) - we need to include it in messages
# maybe it's not perfect - but for this i don't take into account what user set as memory_token_limit
# because (as of now at least) it is intended to add important data - so it's crucial that it is attached fully without any cutting
def prepare_message_content_with_asset_input(message, asset_input):
    # if assetInput is empty - we don't need to do anything
    if isinstance(asset_input, list) and len(asset_input) == 0:
        return message

    logger.info("prepare_messages_with_asset_input")
    existing_text = message['content'][0]['text']
    optimized_data_text = optimize_health_data(asset_input, "csv")
    new_text = f"{existing_text}...\nhere is data:\n{optimized_data_text}"

    # Overwrite the existing content with the new text
    message['content'][0]['text'] = new_text

    return message

# we receive data from DB in json format
# and sometimes we can keep it in json, but mostly we want to move it to CSV
def optimize_health_data(data, format="json") -> str:
    # Define columns to keep
    columns_to_keep = [
        'calendar_date', 'sleep_time_seconds', 'sleep_start', 'sleep_end',
        'nap_time_seconds', 'deep_sleep_seconds', 'light_sleep_seconds', 'rem_sleep_seconds',
        'awake_sleep_seconds', 'average_respiration_value', 'awake_count', 'avg_sleep_stress',
        'sleep_score_feedback', 'overall_score_value', 'overall_score_qualifier',
        'stress_qualifier', 'rem_percentage_value',
        'light_percentage_value', 'deep_percentage_value', 'avg_overnight_hrv',
        'resting_heart_rate', 'body_battery_change', 'restless_moments_count'
    ]

    # Filter data to keep only specified columns
    filtered_data = [{col: day.get(col, '') for col in columns_to_keep} for day in data]

    if format == "json":
        return json.dumps(filtered_data, indent=4)

    # Create CSV-like structure
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns_to_keep)
    writer.writeheader()

    for row in filtered_data:
        writer.writerow(row)

    return output.getvalue().strip()


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
