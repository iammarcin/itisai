from fastapi import HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

import logconfig
import re
import json
import os
from aws.awsProvider import awsProvider
from pathlib import Path

from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings, save


from tempfile import NamedTemporaryFile

logger = logconfig.logger

# little helper class - s3 upload in aws provider was already set and used by other functions
# and it needs file and filename to process the file
class FileWithFilename:
    def __init__(self, file, filename):
        self.file = file
        self.filename = filename


# TODO: turn it into functions to get from API
# but if do so - check main_generators as there is a function to get these voices
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

class ElevenLabsTTSGenerator:
    def __init__(self):
        self.save_to_file = True
        self.save_to_file_iterator = 0
        self.stability = 0.85
        self.similarity_boost = 0.95
        self.format = "mp3"
        self.voice_id = "Sherlock"
        self.eleven_labs_api_voices_url = "https://api.elevenlabs.io/v1/voices"
        self.eleven_labs_api_text_to_speech_url = "https://api.elevenlabs.io/v1/text-to-speech"
        self.eleven_labs_api_billing_url = "https://api.elevenlabs.io/v1/user/subscription"
        self.client = ElevenLabs()

    def set_settings(self, user_settings={}):
        if user_settings:
            # and now process aws settings (doubt it will be used)
            # this is not in use - just for maybe future
            user_settings = user_settings.get("tts", {})
            if "model" in user_settings:
                self.model_name = user_settings["model"]

            if "voice" in user_settings:
                self.voice_id = user_settings["voice"]

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

    def get_voice_id(self, voice_name):
        logger.info("search for voice: %s", voice_name)
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

    async def process_job_request(self, action: str, userInput: dict, assetInput: dict, customerId: int = None, userSettings: dict = {}):
        # OPTIONS
        self.set_settings(userSettings)
        try:
            if action == "tts_no_stream":
                return await self.generate_tts(userInput, customerId)
            elif action == "tts_stream":
                # until i work on stream mode - non stream in use
                return await self.generate_tts(userInput, customerId)
            #    return self.stream_tts(userInput, customerId)
            else:
                raise HTTPException(status_code=400, detail="Unknown action")
        except Exception as e:
            logger.error("Error processing TTS request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing TTS request")

    async def generate_tts(self, userInput: dict, customerId: int = 1):

        try:
            text = self.tune_text(userInput['text'])
            logger.info("TEXT after tunning: %s", text)
            final_voice = self.get_voice_id(self.voice_id)

            audio = self.client.generate(
                text=text,
                voice=Voice(
                    voice_id=final_voice,
                    settings=VoiceSettings(
                        stability=self.stability,
                        similarity_boost=self.similarity_boost,
                        style=0.0,
                        use_speaker_boost=True
                    )
                ),
                model="eleven_monolingual_v1"
            )

            with NamedTemporaryFile(delete=False, suffix=f".{self.format}") as tmp_file:
                save(audio, tmp_file.name)
                tmp_file_path = tmp_file.name

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
