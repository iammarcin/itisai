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
from langchain.document_loaders import UnstructuredURLLoader

logger = logconfig.logger

# this will be place to store all files for customers
baseDir = config.defaults['LOCAL_MAIN_STORAGE']
node_api_endpoint = config.defaults['NODE_API_ENDPOINT']
'''
# this is function to upload final file
async def uploadFinalFile(dir, file, customer_id):
  logger.debug("\n"); logger.debug(
      "!"*30); logger.debug("\n"); logger.debug("UPLOAD"); logger.debug("\n")
  try:
    # upload file
    finalFile = temporaryUpload(dir, file, customer_id)
    if finalFile['success']:
      return { "success": True, "file": finalFile['file'] }
    else:
      # raise exception
      return { "success": False, "error": "Error in uploadFinalFile!!!", "realError": finalFile['realError'] }
  except Exception as e:
    logger.error("Error in uploadFinalFile")
    logger.error(e)
    traceback.print_exc()
    return { "success": False, "error": "Error in uploadFinalFile!!!", "realError": e }


# temporary function - maybe later we put in S3 or something
async def temporaryUpload(dir, file, customer_id):
  try:
    # time now in format YYYYMMDDHHMMSS
    time_now = datetime.now().strftime("%Y%m%d%H%M%S")
    # copy file to baseDir
    dst = os.path.join(baseDir, "uploads", str(customer_id), time_now, file)
    # check if exists, if not create
    if not os.path.exists(os.path.dirname(dst)):
      os.makedirs(os.path.dirname(dst))

    shutil.copyfile(os.path.join(dir,file), dst)

    logger.info(f"Image uploaded to {dst}")
    return { "success": True, "file": dst }
  except Exception as e:
    logger.error("Error in temporaryUpload")
    logger.error(e)
    traceback.print_exc()
    return { "success": False, "error": "Failed to upload image", "realError": e }

# temporary function - maybe later we put in S3 or something
async def temporaryDownload(customer_id, file, requestId):
  # download image from url
  # Make HTTP request to get image data
  try:
    response = requests.get(file)

    # Check if the response was successful
    if response.status_code == 200:
      # Get the file name from the URL
      file_name = os.path.basename(file)
      # destination
      dst = os.path.join(baseDir, "downloads", str(
          customer_id), str(requestId), file_name)
      # check if exists, if not create
      if not os.path.exists(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))

      # Save the image data to the file
      with open(dst, 'wb') as f:
        f.write(response.content)
      logger.info(f"Image saved to {dst}")
      return { "success": True, "file": dst }
    else:
      logger.info("Failed to download image ", file)
      return { "success": False, "error": "Failed to download image", "realError": "response code non 200" }
  except Exception as e:
    logger.error("Error in temporaryDownload")
    logger.error(e)
    traceback.print_exc()
    return { "success": False, "error": "Failed to download image", "realError": e }

# this is function to download all files
async def downloadAllFiles(customer_id, files, requestId):
  logger.debug("\n"); logger.debug(
      "!"*30); logger.debug("\n"); logger.debug("DOWNLOAD"); logger.debug("\n")
  try:
    newFiles = []
    # if empty list (which is OK) - return same list
    if len(files) == 0:
      return { "success": True, "files": files }

    for file in files:
      # download file
      newFile = await temporaryDownload(customer_id, file, requestId)
      if newFile['success']:
        newFiles.append(newFile['file'])
      else:
        # raise exception
        return { "success": False, "error": "Error in downloadAllFiles!!!", "realError": newFile['realError'] }
    return { "success": True, "files": newFiles }
  except Exception as e:
    logger.error("Error in downloadAllFiles")
    logger.error(e)
    traceback.print_exc()
    return { "success": False, "error": "Error in downloadAllFiles!!!", "realError": e }
'''
# upload to S3 through nodejs api
# this works but its slow - so for example in MainImage in react i can use it but need to be careful
# because there is wait for image generation - and poll status every 10 seconds
# so it happened that s3 upload was not finished and there was loop of poll reqs
# i can use it - but have to be sure that s3 upload is finished
# if problem persists - move S3 upload - to SQS request registry (and later s3 upload)
def uploadToS3(file_data, file_name, customer_id, requestId, parentRequestId=None):
  try:
    url = node_api_endpoint + "/" + "sendToS3"

    files = {
        'file': (file_name, BytesIO(file_data), 'rb'),
        'customerId': (None, customer_id),
        'requestId': (None, requestId),
        'parentRequestId': (None, parentRequestId)
    }

    logger.info("uploadToS3 files" + str(files))

    response = requests.post(url, files=files, headers={
                             'x-access-token': config.defaults['SSM_JWT_TOKEN']})
    logger.info("uploadToS3 result" + str(response.text))
    if response.status_code == 200:
      return {"success": True, "code": 200, "message": json.loads(response.text)['message']}
    else:
      return {"success": False, "code": 500, "message": "Error in uploadToS3!!! %s " % str(response)}

  except Exception as e:
    logger.error("Error in uploadToS3")
    logger.error(e)
    traceback.print_exc()
    return {"code": 500, "success": False, "message": "Error in uploadToS3!!! %s " % str(e)}

async def putFilesInStorage(customer_id, files, requestId, action, category, parentRequestId=None):
  try:
      if config.defaults['STORAGE'] == 's3':
        # if files is not empty but string - make it list
        if isinstance(files, str):
            files = [files]

        listOfFilesInS3 = []

        for file in files:
            if file.startswith('http'):
                # remote file, download it
                file_data = requests.get(file).content
                file_name = file.split('/')[-1]

                if "oaidalleapiprodscus.blob.core.windows.net" in file:
                  # this is special case for Dall-e which gives really strange URL
                  # generate random filename with 8 characters - ending on png
                  file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) + ".png"

            else:
                # local file, check if it exists
                if not os.path.exists(file):
                    # this case is for sure local file - so we cannot download it
                    if file.startswith('/') or file.startswith('.'):
                        return {"code": 500, "success": False, "message": "File %s does not exist" % file}
                    # assume it's a remote file (for example URL without http provided)
                    file_data = requests.get(file).content
                    file_name = file.split('/')[-1]
                else:
                    # read the local file
                    with open(file, 'rb') as f:
                        file_data = f.read()
                    file_name = os.path.basename(file)

            response = uploadToS3(file_data, file_name,
                                  customer_id, requestId, parentRequestId)
            if response['success']:
                listOfFilesInS3.append(response['message'])
            else:
                return {"code": 500, "success": False, "message": "Error in putFilesInStorage!!! %s " % str(response)}

        return {"code": 200, "success": True, "message": listOfFilesInS3}

  except Exception as e:
      logger.error("Error in putRemoteFilesInStorage")
      logger.error(e)
      traceback.print_exc()
      return {"code": 500, "success": False, "message": "Error in putRemoteFilesInStorage!!! %s " % str(e)}


async def saveContentToFile(customer_id, content, requestId, fileName=None):
  try:
    # sometimes there will be clear filename provided, but sometimes not
    # lets generate random name - so files are not overwritten
    if fileName is None:
       fileName = ''.join(random.choices(string.ascii_lowercase + string.digits, k = 5))
       fileName = fileName + ".wav"
    # destination
    dst = os.path.join(baseDir, "downloads", str(
        customer_id), str(requestId), fileName)
    # check if exists, if not create
    if not os.path.exists(os.path.dirname(dst)):
      os.makedirs(os.path.dirname(dst))

    # Save the image data to the file
    with open(dst, 'wb') as f:
      f.write(content)

    logger.info(f"File saved to {dst}")
    return { "code": 200, "success": True, "message": dst }
  except Exception as e:
    logger.error("Error in saveBlobToFile")
    logger.error(e)
    traceback.print_exc()
    return { "success": False, "error": "Error in saveBlobToFile!!!", "realError": e }

# download content to file
async def downloadFileFromURL(customer_id, file, requestId):

  # download image from url
  # Make HTTP request to get image data
  try:
    response = requests.get(file)

    # Check if the response was successful
    if response.status_code == 200:
      # Get the file name from the URL
      file_name = os.path.basename(file)
      logger.info("file_name: " + file_name)
      logger.info("file_name: " + file)
      response = await saveContentToFile(customer_id, response.content, requestId, file_name)
      logger.info("response: " + str(response))
      dst = response['message']

      logger.info(f"Image saved to {dst}")
      return {"code": 200, "success": True, "message": dst}
    else:
      logger.info("Failed to download image ", file)
      return {"code": 500, "success": False, "message": "Failed to download file"}
  except Exception as e:
    logger.error("Error in downloadFileFromURL")
    logger.error(e)
    traceback.print_exc()
    return {"code": 500, "success": False, "message": "Failed to download file %s " % str(e)}

# download content and return as processed string (used for example when we input www)
async def downloadContentFromURL(assetInput):
  try:
    for url in assetInput:
      logger.info("MMMM")
      logger.info(url)
      # unstructured doesn't work with txt files in url :(

      if url.endswith('.txt'):
        response = requests.get(url)
        # get content
        text = response.text
      else:
        headers = { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}
        loader=UnstructuredURLLoader(urls = [url], continue_on_failure=False, headers=headers)
        data=loader.load()
        logger.info(data)
        text=data[0].page_content

      '''
      # Download web page content as a Unicode string
      response = requests.get(job_request.url)
      response.encoding = response.apparent_encoding
      content = response.text

      # Use BeautifulSoup to extract text content from HTML
      soup = BeautifulSoup(content, "html.parser")
      text = soup.get_text(separator=" ")
      '''

      logger.debug(text)

      # clean up
      # remove all kinds of white spaces
      text=re.sub(r"\n", " ", text)
      text=re.sub(r"\s+", " ", text)
      text=text.strip()
      return {"code": 200, "success": True, "message": text}
  except Exception as e:
    logger.error("Error in downloadFiles")
    logger.error(e)
    traceback.print_exc()
    if ("404" in str(e)):
      return {"code": 404, "success": False, "message": "Error. Page not found!"}
    return {"code": 500, "success": False, "message": "Error in downloadFiles!!! %s " % str(e)}
