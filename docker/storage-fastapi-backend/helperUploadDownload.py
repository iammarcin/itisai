import traceback
from datetime import datetime
import config
import requests
import random
import string
#from urllib.parse import urlparse
import os, json, re
import logconfig
from io import BytesIO

logger = logconfig.logger

# this will be place to store all files for customers
baseDir = config.defaults['LOCAL_MAIN_STORAGE']

async def saveContentToFile(customer_id, upload_file, requestId, fileName=None):
  try:
    # sometimes there will be clear filename provided, but sometimes not
    # lets generate random name - so files are not overwritten
    if fileName is None:
      date = datetime.now().strftime("%Y%m%d")
      fileName = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 5))
      fileName = date + "_" + fileName + ".mp3"
    # destination
    dst = os.path.join(baseDir, "downloads", str(
        customer_id), str(requestId), fileName)
    # check if exists, if not create
    if not os.path.exists(os.path.dirname(dst)):
      os.makedirs(os.path.dirname(dst))

    # Save the image data to the file
    with open(dst, 'wb') as f:
      f.write(upload_file.file.read())

    logger.info(f"File saved to {dst}")
    return { "code": 200, "success": True, "message": dst }
  except Exception as e:
    logger.error("Error in saveBlobToFile")
    logger.error(e)
    traceback.print_exc()
    return { "success": False, "error": "Error in saveBlobToFile!!!", "realError": e }
