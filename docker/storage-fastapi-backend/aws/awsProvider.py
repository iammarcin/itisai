from fastapi import HTTPException
from fastapi.responses import JSONResponse
import config
from tempfile import NamedTemporaryFile

import logconfig
import re
import os
import shutil
import datetime
import traceback

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logconfig.logger

# AWS S3
s3_client = boto3.client(
    "s3",
    region_name=config.defaults["AWS_REGION"],
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

DEBUG = config.defaults["DEBUG"]
VERBOSE_SUPERB = config.defaults["VERBOSE_SUPERB"]


class awsProvider:
    def __init__(self):
        self.aws_region = "eu-west-1"  # not in use
        self.client = s3_client

    def set_settings(self, user_settings={}):
        if user_settings:
            # and now process aws settings (doubt it will be used)
            # this is not in use - just for maybe future
            user_settings = user_settings.get("aws", {})
            # Update model name
            if "aws_region" in user_settings:
                user_settings["aws_region"] = user_settings["aws_region"]

    async def process_job_request(
        self,
        action: str,
        userInput: dict,
        assetInput: dict,
        customerId: int = None,
        userSettings: dict = {},
    ):
        # OPTIONS
        self.set_settings(userSettings)
        try:
            if action == "s3_upload":
                return await self.s3_upload(action, userInput, assetInput, customerId)
            else:
                raise HTTPException(status_code=400, detail="Unknown action")
        except Exception as e:
            logger.error("Error processing AWS request: %s", str(e))
            raise HTTPException(
                status_code=500, detail="Error processing AWS request")

    async def s3_upload(
        self, action: str, userInput: dict, assetInput: dict, customerId: int = None
    ):
        try:

            # maybe one day will set it in DB
            DISCUSSION_ID = 1
            file = userInput["file"]
            # Validate file type
            filename = file.filename
            allowed_file_types_regex = re.compile(
                r"\.({})$".format(
                    "|".join(config.defaults["ALLOWED_FILE_TYPES"])),
                re.IGNORECASE,
            )
            if not allowed_file_types_regex.search(filename):
                raise HTTPException(
                    status_code=400,
                    detail="Only files with specific extensions are allowed!",
                )

            # Save file temporarily
            with NamedTemporaryFile(delete=False) as tmp:
                shutil.copyfileobj(file.file, tmp)
                tmp_path = tmp.name

            # Create unique file name
            original_filename = filename.replace(" ", "_")
            now = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d")
            random_string = os.urandom(4).hex()
            s3_filename = f"{now}_{random_string}_{original_filename}"
            s3_path = f"{customerId}/assets/chat/{DISCUSSION_ID}/{s3_filename}"

            # Upload to S3
            try:
                with open(tmp_path, "rb") as data:
                    s3_client.upload_fileobj(
                        data,
                        config.defaults["AWS_S3_BUCKET"],
                        s3_path,
                        ExtraArgs={"ACL": "public-read"},
                    )
            except (BotoCoreError, ClientError) as e:
                logger.error("Error uploading file to S3: %s", str(e))
                raise HTTPException(
                    status_code=500, detail="Error uploading file to S3"
                )

            # Clean up temporary file
            os.remove(tmp_path)

            s3_url = f"https://{config.defaults['AWS_S3_BUCKET']}.s3.{config.defaults['AWS_REGION']}.amazonaws.com/{s3_path}"
            logger.info(f"File uploaded successfully to S3: {s3_url}")

            return JSONResponse(
                content={
                    "success": True,
                    "code": 200,
                    "message": {"status": "completed", "result": s3_url},
                },
                status_code=200,
            )

        except Exception as e:
            logger.error("Error in send_to_s3: %s", str(e))
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Error in upload file")
