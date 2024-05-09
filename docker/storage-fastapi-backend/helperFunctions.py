import ffmpeg
import cv2
import os
from PIL import Image
#import math
import shutil
import traceback
from datetime import datetime
import config
import requests

DEBUG = config.defaults['DEBUG']
VERBOSE_SUPERB = config.defaults['VERBOSE_SUPERB']

# this will be place to store all files for customers
baseDir=config.defaults['LOCAL_MAIN_STORAGE']

# settings for ffmpeg
if VERBOSE_SUPERB:
  ffmpegLogLevel='info'
else:
  ffmpegLogLevel='error'

# this is needed for ffmpeg to work later - to concat videos
filesToConcat = []

# this is function to resize single image to given size...
# method:
# resize - just resize to final size
# crop - resize + crop
# DONE
def resizeImage(imageFileName, width, height, outputFileName="output.png", method="resize", dir="./"):
  if DEBUG:
    print("\n"); print("!"*30); print("\n"); print("RESIZE"); print("\n")
  try:
    # Load the input image... merge dir and imageFileName
    img = cv2.imread(os.path.join(dir, imageFileName))

    if method == "resize":
      resized_img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA) # or cv2.INTER_LANCZOS4
    elif method == "crop":
      # Get the original aspect ratio
      original_height, original_width, _ = img.shape
      original_aspect_ratio = original_width / original_height

      # Determine the larger dimension to maintain aspect ratio
      if original_aspect_ratio > width / height:
        new_width = int(height * original_aspect_ratio)
        new_height = height
      else:
        new_width = width
        new_height = int(width / original_aspect_ratio)

      # Resize the image to the larger dimension
      resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

      # Crop the central part of the image
      start_x = (new_width - width) // 2
      start_y = (new_height - height) // 2
      resized_img = resized_img[start_y:start_y+height, start_x:start_x+width]

    # Save the cropped image
    cv2.imwrite(os.path.join(dir, outputFileName), resized_img)
    # verify if file exists
    if not os.path.exists(os.path.join(dir, outputFileName)):
      return { "success": False, "error": "Problem with resizeImage - file not created", "realError": "Problem with resizeImage - file not created" }

    # all success
    if DEBUG:
      print("resizeImage outputFileName", outputFileName)
    return { "success": True, "outputFileName": outputFileName }
  except Exception as e:
    print(e)
    traceback.print_exc()
    return { "success": False, "error": "Problem with resizeImage", "realError": e }

# this is function to concat multiple files (mostly videos) - based on provided list of videos
# inputVideosList - list of videos to concat
def concatFiles(inputVideosList, outputVideoName, dir="./"):
  if DEBUG:
    print("\n"); print("!"*30); print("\n"); print("CONCAT"); print("\n")
  try:
    open(os.path.join(dir, 'concat.txt'), 'w').writelines([('file %s\n' % input_path) for input_path in inputVideosList])
    ffmpeg.input(os.path.join(dir, 'concat.txt'), format='concat', safe=0).output(os.path.join(dir, outputVideoName), c='copy', y=None, loglevel=ffmpegLogLevel).run()
    if DEBUG:
      print("concat outputVideoName", outputVideoName)
    return { "success": True, "outputFileName": outputVideoName }
  except Exception as e:
    print(e)
    traceback.print_exc()
    return { "success": False, "error": "Problem with concatFiles", "realError": e }

# this is to add effect to video
# idea is to have an option - after we merge single image and single mp3 file - to add fade in/out effect
# or alternatively at the end of video - to add fade out effect
def fadeEffect(inputVideoName, outputVideoName, effect="in", length=30, startFrame=0, dir="./"):
  if DEBUG:
    print("\n"); print("!"*30); print("\n"); print("fadeEffect"); print("\n")
  try:
    (
        ffmpeg
        .input(os.path.join(dir, inputVideoName))
        .filter("fade", type=effect, start_frame=startFrame, n=length)
        .output(os.path.join(dir, outputVideoName), y=None, loglevel=ffmpegLogLevel)
        .run()
    )
    if DEBUG:
      print("fadeEffect outputVideoName", outputVideoName)
    return { "success": True, "outputFileName": outputVideoName }
  except Exception as e:
    print(e)
    traceback.print_exc()
    return { "success": False, "error": "Problem with fadeEffect", "realError": e }

# this is to merge video and audio file
# idea is that we will have provided single image, from which we will produce video in length of audio file
# and then we will merge this video with audio file
def mergeAudioVideo(inputVideoName, inputAudioName, outputVideoName, dir="./"):
  if DEBUG:
    print("\n"); print("!"*30); print("\n"); print("MERGE AUDIO VIDEO"); print("\n")  
  try:
    input_video = ffmpeg.input(os.path.join(dir, inputVideoName))
    input_audio = ffmpeg.input(os.path.join(dir, inputAudioName))
    ffmpeg.concat(input_video, input_audio, v=1, a=1).output(os.path.join(dir, outputVideoName), y=None, loglevel=ffmpegLogLevel).run()
    if DEBUG:
      print("merge outputVideoName", outputVideoName)
    return { "success": True, "outputFileName": outputVideoName }
  except Exception as e:
    print(e)
    traceback.print_exc()
    return { "success": False, "error": "Problem with mergeAudioVideo", "realError": e }

# to generate proper video from single image - to have proper length - based on audio file
# idea is to later merge this video with audio file
def getDurationOfAudioFile(inputAudioName, dir="./"):
  if DEBUG:
    print("\n"); print("!"*30); print("\n"); print("getAudioDuration"); print("\n")
  try:
    probe = ffmpeg.probe(os.path.join(dir, inputAudioName))
    video_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
    duration = float(video_info['duration'])
    if DEBUG:
      print("duration", duration)
    return { "success": True, "duration": duration }
  except Exception as e:
    print("TOTOTOTOTOTOTO")
    print(e)
    traceback.print_exc()
    return { "success": False, "error": "Problem with getDurationOfAudioFile", "realError": e }

# this is to generate video from single image - to have proper length - based on audio file
# duration of audio file we will get from different function
# method :
# zoomCenter - zoom in center of image
# zoomTopLeft - zoom in top left of image (more fluid)
# noZoom - no zoom - just create a video from file
def generateZoomVideo(filename, videoLength, width, height, outputFileName="output.mp4", method="zoomCenter", dir="./"):
  if DEBUG:
    print("\n"); print("!"*30); print("\n"); print("zoom Video"); print("\n")
  try:
    # Calculate the number of frames
    frames = int(videoLength * 30)

    # Calculate the zoom step size
    zoomSteps = (1.2 - 1.001) / frames
    zoomSteps = max(min(zoomSteps, 0.002), 0.001)

    # Calculate the starting zoom value
    startingZoom = 1.2
    while frames * zoomSteps < (1.2 - 1.001):
        startingZoom += 0.001
        zoomSteps = (startingZoom - 1.001) / frames

    # Calculate the zoom formula
    zoom_formula = f"if(lte(zoom,1.0),{startingZoom},max(1.001,zoom-{zoomSteps}))"
    xValue=yValue=0
    if method == "zoomCenter":
      xValue="iw/2-(iw/zoom/2)"
      yValue="ih/2-(ih/zoom/2)"
    elif method == "noZoom":
      zoom_formula = "1"

    if method == "zoomCenter" or method == "zoomTopLeft" or method == "noZoom":
      # Generate the video with the zoom effect
      try:
        ffmpeg.input(os.path.join(dir, filename), framerate=30) \
            .filter("zoompan", zoom=zoom_formula, d=frames, s=f"{width}x{height}", x=xValue, y=yValue) \
            .output(os.path.join(dir, outputFileName), c="libx264", r=30, pix_fmt="yuv420p", y=None, loglevel=ffmpegLogLevel) \
            .run()
      except Exception as e:
        print(e)
        traceback.print_exc()
        return { "success": False, "error": "Problem with generateZoomVideo!!!!!!!", "realError": e }
    else:
      return { "success": False, "error": "Wrong method provided", "realError": "Wrong method provided" }
    print("OK2")
    if DEBUG:
      print("zoom Video - end")
      print(outputFileName)
    return { "success": True, "outputFileName": outputFileName }
  except Exception as e:
    print(e)
    traceback.print_exc()
    return { "success": False, "error": "Problem with generateZoomVideo!", "realError": e }

# verify if directory exists - if not - create it
# DONE
def verifyDirectory(dirName):
  try:
    if not os.path.exists(dirName):
      os.makedirs(dirName)
    return { "success": True }
  except Exception as e:
    print(e)
    traceback.print_exc()
    return { "success": False, "error": "Problem with verifyDirectory", "realError": e }

# copy provided list of files to directory
# DONE
def copyFilesToDirectory(filesList, dirName):
  print(filesList)
  print(dirName)
  try:
    namesOnly = []
    for file in filesList:
      shutil.copy(file, dirName)
      namesOnly.append(os.path.basename(file))
    return { "success": True, "namesOnly": namesOnly }
  except Exception as e:
    print(e)
    traceback.print_exc()
    return { "success": False, "error": "Problem with copyFilesToDirectory", "realError": e }

# consistency check for provided data
# output:
# version 1 - if there is same number of files
# version 2 - if there is single audio and multiple images
# version 3 - if there is single image and multiple audio files
# version 4 - if there is no image files
# version 5 - if there is no audio files
# DONE
def consistencyCheck(imgFiles, audioFiles):
  try:
    if VERBOSE_SUPERB:
      print("consistencyCheck")
      print("imgFiles", imgFiles)
      print("audioFiles", audioFiles)
      print(type(imgFiles))
      print(type(audioFiles))
    # first check variant of use case - if there is same number of files or not
    if len(imgFiles) != len(audioFiles):
      if len(imgFiles) == 0:
        return { "success": True, "version": 4 }
      elif len(audioFiles) == 0:
        return { "success": True, "version": 5 }
      elif len(imgFiles) == 1:
        return { "success": True, "version": 3 }
      # honestly ignoring cases where there are multiple images and more then 1 audio (but different number)
      return { "success": True, "version": 2 }
    # then make sure there is at least one file to process
    if len(imgFiles) == 0 and len(audioFiles) == 0:
      return { "success": False, "error": "No image files provided", "realError": "No image files provided" }
    return { "success": True, "version": 1 }
  except Exception as e:
    print(e)
    traceback.print_exc()
    return { "success": False, "error": "Problem with consistencyCheck", "realError": e }

# in case no resize - we need to get current image size
# because in generateZoomVideo we need to know the size of image
# DONE
def getImageSize(item):
  try:
    img = Image.open(item)
    return img.size
  except Exception as e:
    print(e)
    traceback.print_exc()
    return { "success": False, "error": "Problem with getImageSize", "realError": e }


# SIMPLIFICATION FUNCTIONS
# this is common part for all versions of use cases
# we take single image, we resize, generate video and add optional fade in effect
def processSingleImage(dirName, idx, fileName, width, height, duration, resizeImgMethod, generateZoomVideoMethod, fadeEffectType, fadeEffectLength=0, fadeEffectStartFrame=0):
  ERROR=False
  ERRORMSG=""
  REALERRORMSG=""
  finalFileName=""
  # FIRST RESIZE
  # add prefix to file name
  tempFileName = f"{idx}_resized_{fileName}"
  if resizeImgMethod == "none":
    resize = { "success": True, "outputFileName": fileName }
  else:
    resize=resizeImage(fileName, width, height, outputFileName=tempFileName, method=resizeImgMethod, dir=dirName)
  if resize["success"]:
    tempFileName = f"{idx}_zoom_{os.path.basename(fileName)}.mp4"
    zoomVideo=generateZoomVideo(resize["outputFileName"], duration, width, height, method=generateZoomVideoMethod, dir=dirName, outputFileName=tempFileName)
    if zoomVideo["success"]:
      finalFileName = zoomVideo["outputFileName"]
      if fadeEffectType != "none":
        tempFileName = f"{idx}_fade_{os.path.basename(fileName)}.mp4"
        fade=fadeEffect(zoomVideo["outputFileName"], tempFileName, effect=fadeEffectType, length=fadeEffectLength, startFrame=fadeEffectStartFrame, dir=dirName)
        if fade["success"]:
          finalFileName = fade["outputFileName"]
        else:
          ERROR=True
          ERRORMSG=fade["error"]
          REALERRORMSG=fade["realError"]
    else:
        ERROR=True
        ERRORMSG=zoomVideo["error"]
        REALERRORMSG=zoomVideo["realError"]
  else:
    ERROR=True
    ERRORMSG=resize["error"]
    REALERRORMSG=resize["realError"]

  if ERROR:
    return { "success": False, "error": ERRORMSG, "realError": REALERRORMSG }
  else:
    return { "success": True, "outputFileName": finalFileName }


#final API function
# params:
# imgFiles - list of image files
# audioFiles - list of audio files
# width - width of output video
# height - height of output video
# resizeImgMethod - method of resizing image - "resize", "crop" or "none"
# generateZoomVideoMethod - method of generating video from image - "zoomCenter", "zoomTopLeft", "noZoom"
# fadeEffectType - type of fade effect - "in", "out", "none"
# fadeEffectLength - length of fade effect in frames
# fadeEffectStartFrame - start frame of fade effect
# customerId - id of customer
# duration - duration of video in seconds (if audio file is provided - this value will be ignored)
def processFiles(imgFiles=[], audioFiles=[], width=1024, height=1024, resizeImgMethod="resize", generateZoomVideoMethod="noZoom", fadeEffectType="in", fadeEffectLength=30, fadeEffectStartFrame=0, duration=5, customerId=1):
  if DEBUG:
    print("Processing files")
  ERROR=False
  ERROR_MSG=""
  REALERRORMSG=""
  finalFileName=""
  consistency=consistencyCheck(imgFiles, audioFiles)
  if consistency["success"]:
    version=consistency["version"]
  else:
    return { "success": False, "error": "No valid files provided", "realError": consistency["error"] }

  # current datetime in format YYYYMMDDHHMMSS
  now = datetime.now().strftime("%Y%m%d%H%M%S")

  dirName=f"{baseDir}/{customerId}/{now}/"
  # verify if dir exists
  verifyDirectory(dirName)
  # copy files
  copyImgFiles=copyFilesToDirectory(imgFiles, dirName)
  copyAudioFiles=copyFilesToDirectory(audioFiles, dirName)

  # till now we deal with full path of files - so that can be copied properly.. from now on we deal with names only (because dif is another parameter)
  if copyImgFiles["success"]:
    imgFiles=copyImgFiles["namesOnly"]
  else:
    return { "success": False, "error": "Problem with copying image files", "realError": copyImgFiles["error"] }
  if copyAudioFiles["success"]:
    audioFiles=copyAudioFiles["namesOnly"]
  else:
    return { "success": False, "error": "Problem with copying audio files", "realError": copyAudioFiles["error"] }

  if DEBUG:
    print("\n"); print("!"*30); print("\n"); print("\n")
    print("All good. Lets start!")

  filesToConcat=[]

  # here we assume already that number of files is the same (after consistency check above)
  for idx,item in enumerate(imgFiles):
    # in most cases we want to proceed to processing single image
    # only exception is when there is no image file obviously
    proceedWithSingleImage=True
    # depending on number of files (version) - we take duration from different source
    if version == 1: # there are same number of files for audio and video
      durationRes=getDurationOfAudioFile(audioFiles[idx],dirName)
    elif version == 2: # there are multiple images and single audio
      durationRes=getDurationOfAudioFile(audioFiles[0],dirName)
    elif version == 3: # there is only 1 image file
      # loop through all audio files and sum up duration
      duration=0
      for audioFile in audioFiles:
        durationRes=getDurationOfAudioFile(audioFile,dirName)
        if durationRes["success"]:
          duration+=durationRes["duration"]
        else:
          ERROR=True
          ERROR_MSG=durationRes["error"]
          REALERRORMSG=durationRes["realError"]
          return { "success": False, "error": ERROR_MSG, "realError": REALERRORMSG }
      # now lets merge all audio files into one
      concat=concatFiles(audioFiles, "concat.mp4", dirName)
      if concat["success"] == False:
        ERROR=True
        ERROR_MSG=durationRes["error"]
        REALERRORMSG=durationRes["realError"]
        return { "success": False, "error": ERROR_MSG, "realError": REALERRORMSG }

      durationRes={"success": True, "duration": duration}
    elif version == 4: # only audio file(s)
      proceedWithSingleImage=False
    elif version == 5: # if there is no audio - we take standard or provided value
      durationRes={"success": True, "duration": duration}
    else:
      ERROR=True
      ERROR_MSG="Wrong version"
      REALERRORMSG="Wrong version"
      return { "success": False, "error": ERROR_MSG, "realError": ERROR_MSG }

    if durationRes["success"] and proceedWithSingleImage:
      duration=durationRes["duration"]
      # if there is 1 audio file - we want to fit all images to this audio file duration
      if version == 2:
        duration=duration/len(imgFiles)

      if resizeImgMethod == "none":
        # get width and height of image
        width, height = getImageSize(item)
      resProcessImage = processSingleImage(dirName, idx, item, width, height, duration, resizeImgMethod, generateZoomVideoMethod, fadeEffectType, fadeEffectLength, fadeEffectStartFrame)
      if resProcessImage["success"]:
        # if its version 1 (1 audio file per image) - we need to merge with audio
        if version == 1 or version == 3:
          tempFileName = f"{idx}_audio_{os.path.basename(item)}.mp4"

          if version == 3:
            audioName="concat.mp4"
            tempFileName = "finalOutput.mp4"
          else:
            audioName=audioFiles[idx]

          mergeAudio=mergeAudioVideo(resProcessImage["outputFileName"], audioName, tempFileName, dir=dirName)
          if mergeAudio["success"]:
            filesToConcat.append(mergeAudio["outputFileName"])
          else:
            ERROR=True
            ERROR_MSG=mergeAudio["error"]
            REALERRORMSG=mergeAudio["realError"]
            break
        elif version == 2 or version == 3 or version == 5:
          filesToConcat.append(resProcessImage["outputFileName"])
      else:
        ERROR=True
        ERROR_MSG=resProcessImage["error"]
        REALERRORMSG=resProcessImage["realError"]
        break
    else:
      ERROR=True
      ERROR_MSG=durationRes["error"]
      REALERRORMSG=durationRes["realError"]
      break

  # special case for version 4 (only audio files)
  if version == 4:
    filesToConcat = audioFiles

  # if there are files to concat
  if len(filesToConcat) > 0:
    fileNameCurrent="finalOutput.mp4"
    # if this is version 2 (1 audio file) - this is not final file - as we need to merge it
    if version == 2:
      fileNameCurrent="outputForAudio.mp4"
    # if there's only 1 file - we don't need to concat
    if len(filesToConcat) == 1:
      concat={"success": True, "outputFileName": filesToConcat[0]}
    else:
      concat=concatFiles(filesToConcat, fileNameCurrent, dir=dirName)
    if concat["success"]:
      finalFileName=concat["outputFileName"]
      # if this is version 2 (1 audio file) - lets merge now - after concat
      if version == 2:
        fileNameCurrent="finalOutput.mp4"
        # we need to merge audio and video
        merge=mergeAudioVideo(finalFileName, audioFiles[0], fileNameCurrent, dir=dirName)
        if merge["success"]:
          finalFileName=merge["outputFileName"]
        else:
          ERROR=True
          ERROR_MSG=merge["error"]
          REALERRORMSG=merge["realError"]
    else:
      ERROR=True
      ERROR_MSG=concat["error"]
      REALERRORMSG=concat["realError"]

  if ERROR:
    return { "success": False, "error": ERROR_MSG, "realError": REALERRORMSG }

  if DEBUG:
    print("All good. Finished!")
  
  return { "success": True, "finalDir": dirName, "finalFile": finalFileName }

'''
###################################
# CONFIG
dirName="/Users/marcinniskiewicz/dev/git/priv/contentAutomation/ffmpegTests/mn2026"
imgFiles=["3.png", "4.png", "5.png"]
audioFiles = [ "4.mp3"]
width=1024
height=1024
resizeImgMethod="resize" # "crop"
generateZoomVideoMethod="noZoom" # "zoomTopLeft"
fadeEffectType="in"
fadeEffectLength=30
fadeEffectStartFrame=0
###################################

'''