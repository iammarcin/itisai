from fastapi import HTTPException, Response
from fastapi.responses import StreamingResponse, JSONResponse

import requests
import traceback
import logconfig
import re
import json
import os
from aws.awsProvider import awsProvider

from tempfile import NamedTemporaryFile

logger = logconfig.logger

# little helper class - s3 upload in aws provider was already set and used by other functions
# and it needs file and filename to process the file
class FileWithFilename:
    def __init__(self, file, filename):
        self.file = file
        self.filename = filename


# TODO: turn it into functions to get from API
availableVoices = [
    {"voice_id": "OQxYoOfpAUkG05J0ccwK", "name": "Sherlock", },
    {"voice_id": "30zc5PfKKHzfXQfjXbLU", "name": "Naval", },
    {"voice_id": "VXeKt8WY8XxvvuAzPcBq", "name": "Yuval", },
    {"voice_id": "N1LkSFjuhW6TRodJYBhu", "name": "Elon", },
    {"voice_id": "IlULyVcJD5RzBQR0n2LG", "name": "Hermiona", },
    {"voice_id": "2hYX7DThVWR7WT2BGQ3N", "name": "David", },
    {"voice_id": "QIhQcQqeyCWyOPuE7kv9", "name": "Shaan", },
    {"voice_id": "tRT6MMJIOgJI7oSILj0I", "name": "Rick", },
    {"voice_id": "0P79HLgfttzosL3iYbb5", "name": "Morty", },
    {"voice_id": "a5l5z8A3DCH5XmSdNGyS", "name": "Samantha", },
    {"voice_id": "NwcIoUSR50GT4NXePX5l", "name": "MyVoiceAmericanWoman1", },
    {"voice_id": "vKqkldqRlIKEBthZUkwj", "name": "MyVoiceAmerican1", },
    {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", },
    {"voice_id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", },
    {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", },
    {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni", },
    {"voice_id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli", },
    {"voice_id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh", },
    {"voice_id": "VR6AewLTigWG4xSOukaG", "name": "Arnold", },
    {"voice_id": "pNInz6obpgDQGcFmaJgB", "name": "Adam", }]

class ElevenLabsAudioGenerator:
    def __init__(self, eleven_labs_api_key):
        self.eleven_labs_api_key = eleven_labs_api_key
        self.save_to_file = True
        self.save_to_file_iterator = 0
        self.stability = 0.85
        self.similarity_boost = 0.95
        self.voice_id = "Sherlock"
        self.eleven_labs_api_voices_url = "https://api.elevenlabs.io/v1/voices"
        self.eleven_labs_api_text_to_speech_url = "https://api.elevenlabs.io/v1/text-to-speech"
        self.eleven_labs_api_billing_url = "https://api.elevenlabs.io/v1/user/subscription"

    def set_settings(self, user_settings={}):
        if user_settings:
            # and now process aws settings (doubt it will be used)
            # this is not in use - just for maybe future
            user_settings = user_settings.get("tts", {})
            if "model" in user_settings:
                self.model_name = user_settings["model"]

            if "voice" in user_settings:
                self.voice = user_settings["voice"]

            if "format" in user_settings:
                self.format = user_settings["format"]

            if "streaming" in user_settings:
                self.streaming = user_settings["streaming"]

            if "speed" in user_settings:
                self.speed = user_settings["speed"]

            if "stability" in user_settings:
                self.stability = user_settings["stability"]

            if "similarity_boost" in user_settings:
                self.similarity_boost = user_settings["similarity_boost"]

    # getter and setter for save_to_file variable
    def get_save_to_file(self):
        return self.save_to_file

    def set_save_to_file(self, save_to_file):
        self.save_to_file = save_to_file

    # getter and setter for save_to_file_iterator variable
    def get_save_to_file_iterator(self):
        return self.save_to_file_iterator

    def set_save_to_file_iterator(self, save_to_file_iterator):
        self.save_to_file_iterator = save_to_file_iterator

    def save2file(self, content, customerId, requestId):
        self.save_to_file_iterator += 1
        filename = f"output_{self.save_to_file_iterator}.mp3"
        # save to /storage/testApi/1
        filename = f"/storage/testApi/{customerId}/{requestId}/{filename}"

        try:
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
            with open(filename, "wb") as f:
                f.write(content)
        except:
            print("Error writing file")
            return False
        return filename

    def get_voice_id(self, voice_name):
        for voice in availableVoices:
            if voice_name == voice["name"]:
                return voice["voice_id"]
            else:
                if voice_name == voice["voice_id"]:
                    return voice["voice_id"]
        # if nothing works - return first voice
        return availableVoices[0]["voice_id"]

    def tune_text(self, text):
        # replace comma with two dots in text
        text = text.replace(",", ".. …")
        text = text.replace("?!", "??")

        # Find any single period at the end of sentence followed by a space
        pattern = r"([a-zA-Z])\. "
        text = re.sub(pattern, r"\1.. ", text)
        # same with exclamation mark
        pattern = r"([a-zA-Z])\! "
        text = re.sub(pattern, r"\1!!.. ", text)
        # same with question mark
        pattern = r"([a-zA-Z])\? "
        text = re.sub(pattern, r"\1??.. ", text)
        return text

    def billing(self):
        url = self.eleven_labs_api_billing_url
        headers = {
            "xi-api-key": self.eleven_labs_api_key
        }
        # response = requests.get(url, headers=headers)
        response = {
            "tier": "creator",
            "character_count": 54211,
            "character_limit": 100000,
            "can_extend_character_limit": True,
            "allowed_to_extend_character_limit": True,
            "next_character_count_reset_unix": 1678630692,
            "voice_limit": 30,
            "professional_voice_limit": 1,
            "can_extend_voice_limit": False,
            "can_use_instant_voice_cloning": True,
            "can_use_professional_voice_cloning": True,
            "available_models": [
                {
                    "model_id": "prod",
                    "display_name": "Prod",
                    "supported_language": [
                        {
                            "iso_code": "en-us",
                            "display_name": "English"
                        }
                    ]
                }
            ],
            "can_use_delayed_payment_methods": False,
            "currency": "usd",
            "status": "active",
            "next_invoice": {
                "amount_due_cents": 2200,
                "next_payment_attempt_unix": 1683829646
            }
        }

        import time

        # Get the current UNIX timestamp
        now = int(time.time())

        # Get the UNIX timestamp of the next character count reset
        reset_unix = response['next_invoice']['next_payment_attempt_unix']

        # Calculate the number of seconds until the reset
        seconds_until_reset = reset_unix - now

        # Calculate the number of days until the reset
        days_until_reset = seconds_until_reset // (60 * 60 * 24)

        # with hours
        # Calculate the number of seconds until the reset
        seconds_until_reset = reset_unix - now

        # Calculate the number of days, hours, and minutes until the reset
        days_until_reset = seconds_until_reset // (60 * 60 * 24)
        hours_until_reset = (seconds_until_reset % (60 * 60 * 24)) // (60 * 60)
        minutes_until_reset = (seconds_until_reset % (60 * 60)) // 60

        # Format the result as a string
        result = f"There are {days_until_reset} days, {hours_until_reset} hours, and {minutes_until_reset} minutes until the next character count reset."

        print(result)

        print(f"There are {days_until_reset} days until the next character count reset.")

        if response.status_code == 200:
            return response.json()
        else:
            return response.text

    def voice_settings(self, voice_id, stability=None, similarity_boost=0.95):
        voice_id = self.get_voice_id(voice_id)
        if stability is None:
            self.eleven_labs_api_url = "https://api.elevenlabs.io/v1/voices"
            # get current settings
            url = f"{self.eleven_labs_api_voices_url}/{voice_id}/settings"
            headers = {
                "xi-api-key": self.eleven_labs_api_key
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                return response.text
        else:
            # edit settings
            url = f"{self.eleven_labs_api_voices_url}/{voice_id}/settings/edit"
            headers = {
                "xi-api-key": self.eleven_labs_api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.text
            else:
                return response.text

    async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, userSettings: dict = {}):
        # OPTIONS
        self.set_settings(userSettings)
        try:
            if action == "tts_no_stream":
                return await self.generate_tts(userInput, customerId)
            # elif action == "tts_stream":
            #    return self.stream_tts(userInput, customerId)
            else:
                raise HTTPException(status_code=400, detail="Unknown action")
        except Exception as e:
            logger.error("Error processing TTS request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing TTS request")

    async def generate_tts(self, userInput: dict, customerId: int = 1):
        try:
            text = userInput["text"]

            # fail on purpose
            # test = userInput['test']

            # url = "https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

            final_voice = self.get_voice_id(self.voice_id)
            response = requests.post(f"{self.eleven_labs_api_text_to_speech_url}/{final_voice}", headers=headers, json=payload)

            payload = {
                "text": text,
                "model_id": "<string>",
                "voice_settings": {
                    "stability": 123,
                    "similarity_boost": 123,
                    "style": 123,
                    "use_speaker_boost": True
                },
                "pronunciation_dictionary_locators": [
                    {
                        "pronunciation_dictionary_id": "<string>",
                        "version_id": "<string>"
                    }
                ],
                "seed": 123,
                "previous_text": "<string>",
                "next_text": "<string>",
                "previous_request_ids": ["<string>"],
                "next_request_ids": ["<string>"]
            }
            headers = {"Content-Type": "application/json"}

            response = requests.request("POST", url, json=payload, headers=headers)

            print(response.text)

            response = self.client.audio.speech.create(
                model=self.model_name,
                voice=self.voice,
                speed=self.speed,
                response_format=self.format,
                input=text,
            )

            with NamedTemporaryFile(delete=False, suffix=f".{self.format}") as tmp_file:
                tmp_file_path = tmp_file.name
                response.stream_to_file(tmp_file_path)

            with open(tmp_file_path, "rb") as tmp_file:
                file_with_filename = FileWithFilename(
                    tmp_file, Path(tmp_file_path).name)
                logger.info("Uploading TTS to S3")
                logger.info(file_with_filename)
                s3_response = await awsProvider.s3_upload(
                    awsProvider,
                    action="s3_upload",
                    userInput={"file": file_with_filename},
                    assetInput={},
                    customerId=customerId
                )

            s3_response_content = json.loads(s3_response.body.decode("utf-8"))
            logger.info("s3_response_content %s", s3_response_content)
            s3_url = s3_response_content["message"]["result"]

            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": s3_url}}, status_code=200)
        except Exception as e:
            logger.error("Error generating TTS: %s", str(e))
            raise HTTPException(status_code=500, detail="Error generating TTS")

    async def generateOLD(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, requestId: int = None, userSettings: dict = {}, returnTestData: bool = False):
        logger.debug("ElevenLabsAudioGenerator.text_to_speech() called")

        if returnTestData:
            return {'code': 200, 'success': True, 'message': {"status": "completed", "result_type": "ready_file", "result": "/storage/testApi/11/1225/output_1.mp3"}}

        # tune text a bit - so emotions are better
        text = self.tune_text(userInput['prompt'])
        headers = {
            "xi-api-key": self.eleven_labs_api_key
        }
        payload = {
            "text": text,
        }
        final_voice = self.get_voice_id(self.voice_id)

        self.voice_settings(final_voice, stability=self.stability, similarity_boost=self.similarity_boost)

        logger.info(f"voice_id chosen: {final_voice}")

        try:
            response = requests.post(f"{self.eleven_labs_api_text_to_speech_url}/{final_voice}", headers=headers, json=payload)
            logger.info(f"ElevenLabsAudioGenerator.text_to_speech() - response: {response}")
            if response.status_code == 200:
                filename = None
                if self.save_to_file:
                    filename = self.save2file(response.content, customerId, requestId)

                logger.debug("ElevenLabsAudioGenerator.text_to_speech() - success")

                return {'code': 200, 'success': True, 'message': {"status": "completed", "result_type": "ready_file", "result": filename}}
            else:
                logger.error(f"ElevenLabsAudioGenerator.text_to_speech() -  error")
                logger.error(response.text)
                raise HTTPException(status_code=response.status_code, detail=json.loads(response.text)['detail'])
        except HTTPException as e:
            logger.error("Error while making API call to ElevenLabs - HTTPException ")
            logger.error(e)
            return {'code': e.status_code, 'success': False, 'message': e.detail}
        except Exception as e:
            logger.error("Error while making API call to ElevenLabs - exception ")
            logger.error(e)
            traceback.print_exc()
            return {'code': 500, 'success': False, 'message': str(e)}
