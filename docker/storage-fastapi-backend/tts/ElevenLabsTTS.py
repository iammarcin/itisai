from fastapi import HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

import logconfig
import json
from aws.awsProvider import awsProvider
from tts.ttsHelpers import *

from pathlib import Path

from elevenlabs.client import ElevenLabs, BaseElevenLabs
from elevenlabs import Voice, VoiceSettings, save

from tempfile import NamedTemporaryFile
import config as config
logger = logconfig.logger

VERBOSE_SUPERB = config.defaults['VERBOSE_SUPERB']

# little helper class - s3 upload in aws provider was already set and used by other functions
# and it needs file and filename to process the file
class FileWithFilename:
    def __init__(self, file, filename):
        self.file = file
        self.filename = filename


# TODO: turn it into functions to get from API
# but if do so - check main_generators as there is a function to get these voices
availableVoices = [
    {"voice_id": "ywZw8GayBRRkuqUnUGhk", "name": "Sherlock", },
    {"voice_id": "Fd0tSzlmsvLr5hseQNC5", "name": "Naval", },
    {"voice_id": "Pr8yZ8kUAqVppjka91Ip", "name": "Yuval", },
    {"voice_id": "xZNdnt7SgqbwFCk9fva3", "name": "Elon", },
    {"voice_id": "IlULyVcJD5RzBQR0n2LG", "name": "Hermiona", },
    {"voice_id": "kOqEtFu394L4slr6R3ld", "name": "David", },
    {"voice_id": "QIhQcQqeyCWyOPuE7kv9", "name": "Shaan", },
    {"voice_id": "5AZpUXZFKLKyfeZerS7c", "name": "Rick", },
    {"voice_id": "0P79HLgfttzosL3iYbb5", "name": "Morty", },
    {"voice_id": "a5l5z8A3DCH5XmSdNGyS", "name": "Samantha", },
    {"voice_id": "xctasy8XvGp2cVO9HL9k", "name": "Allison", },  # quite energetic
    {"voice_id": "ZF6FPAbjXT4488VcRRnw", "name": "Amelia", },  # UK, quite energetic
    {"voice_id": "FVQMzxJGPUBtfz1Azdoy", "name": "Danielle", },  # rather calm
    {"voice_id": "OYTbf65OHHFELVut7v2H", "name": "Hope", },  # natural US
    {"voice_id": "Xb7hH8MSUJpSbSDYk0k2", "name": "Alice", },
    {"voice_id": "pqHfZKP75CvOlQylNhV4", "name": "Bill", },
    {"voice_id": "nPczCjzI2devNBz1zQrb", "name": "Brian", },
    {"voice_id": "cjVigY5qzO86Huf0OWal", "name": "Eric", },
    {"voice_id": "cgSgspJ2msm6clMCkdW9", "name": "Jessica", },
    {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Sarah", },
    {"voice_id": "bIHbv24MWmeRgasZH58o", "name": "Will", }]

class ElevenLabsTTSGenerator:
    def __init__(self):
        self.model_name = "eleven_monolingual_v1"
        self.available_models = ["eleven_monolingual_v1", "eleven_multilingual_v2", "eleven_turbo_v2_5", "eleven_turbo_v2"]
        self.save_to_file = True
        self.save_to_file_iterator = 0
        self.stability = 0.85
        self.similarity_boost = 0.95
        self.style_exaggeration = 0  # affects latency, should remain 0 in most cases
        self.speaker_boost = False  # affects latency, rather subtle changes
        self.sound_effects_duration = 10  # max - 22
        self.sound_effects_prompt_influence = 0.3
        self.format = "mp3"
        self.voice_id = "Sherlock"
        self.client = ElevenLabs()

    def set_settings(self, user_settings={}):
        if user_settings:
            # and now process aws settings (doubt it will be used)
            # this is not in use - just for maybe future
            user_settings = user_settings.get("tts", {})

            if "model" in user_settings:
                model = user_settings["model"]
                if model == 'english':
                    self.model_name = "eleven_monolingual_v1"
                elif model == "multi":
                    self.model_name = "eleven_multilingual_v2"
                elif model == "turbo":
                    self.model_name = "eleven_turbo_v2_5"
                else:
                    self.model_name = "eleven_monolingual_v1"

            if "voice" in user_settings:
                # make sure that first letter is capital, but rest is small
                self.voice_id = user_settings["voice"].capitalize()

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

            if "style_exaggeration" in user_settings:
                self.style_exaggeration = user_settings["style_exaggeration"]

            if "speaker_boost" in user_settings:
                self.speaker_boost = user_settings["speaker_boost"]

    def get_voice_id(self, voice_name):
        voice_name = voice_name.capitalize()
        logger.info("search for voice: %s", voice_name)
        for voice in availableVoices:
            if voice_name == voice["name"]:
                return voice["voice_id"]
            else:
                if voice_name == voice["voice_id"]:
                    return voice["voice_id"]
        # if nothing works - return first voice
        return availableVoices[0]["voice_id"]

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
            elif action == "sound_effect":
                return await self.generate_sound_effect(userInput, customerId)
            elif action == "billing":
                return await self.billing(userInput, customerId)
            else:
                raise HTTPException(status_code=400, detail="Unknown action")
        except Exception as e:
            logger.error("Error processing TTS request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing TTS request")

    async def generate_tts(self, userInput: dict, customerId: int = 1):

        try:
            text = tune_text(userInput['text'])
            logger.info("TEXT after tunning: %s", text)
            final_voice = self.get_voice_id(self.voice_id)

            audio = self.client.generate(
                text=text,
                voice=Voice(
                    voice_id=final_voice,
                    settings=VoiceSettings(
                        stability=self.stability,
                        similarity_boost=self.similarity_boost,
                        style=self.style_exaggeration,
                        use_speaker_boost=self.speaker_boost
                    )
                ),
                model=self.model_name
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

    async def generate_sound_effect(self, userInput: dict, customerId: int = 1):
        try:
            text = userInput['text']
            # TODO test with null - or without providing parameter
            duration_seconds = userInput.get("duration_seconds", None)
            prompt_influence = userInput.get("prompt_influence", 0.3)

            result = self.client.text_to_sound_effects.convert(
                text=text,
                duration_seconds=duration_seconds,
                prompt_influence=prompt_influence
            )

            with NamedTemporaryFile(delete=False, suffix=f".{self.format}") as tmp_file:
                for chunk in result:
                    tmp_file.write(chunk)
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

    async def billing(self, userInput: dict, customerId: int = 1):

        try:
            client = BaseElevenLabs()
            billing = client.user.get_subscription()

            if VERBOSE_SUPERB:
                logger.info("billing data:")
                logger.info(billing)

            character_count = billing.character_count
            character_limit = billing.character_limit
            logger.info(billing.next_character_count_reset_unix)
            next_character_count_reset_unix = convert_timestamp_to_date(billing.next_character_count_reset_unix)
            # 1723830408
            logger.info(next_character_count_reset_unix)

            return JSONResponse(content={"success": True, "code": 200, "message": {"status": "completed", "result": {"character_count": character_count, "character_limit": character_limit, "next_billing_date": next_character_count_reset_unix}}}, status_code=200)
        except Exception as e:
            logger.error("Error generating TTS: %s", str(e))
            raise HTTPException(status_code=500, detail="Error generating TTS")
