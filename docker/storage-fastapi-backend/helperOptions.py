import config

def getDefaultOptions(category):

  defaultTextOptions = {

  }

  defaultImageOptions = {
  }

  defaultAudioOptions = {
  }

  defaultSpeechOptions = {
  }

  defaultVideoOptions = {
  } 

  defaultOptions = {
    'text': defaultTextOptions,
    'image': defaultImageOptions,
    'audio': defaultAudioOptions,
    'speech': defaultSpeechOptions,
    'video': defaultVideoOptions,
  }
  
  if category not in defaultOptions:
    return None
  elif category == "all":
    return defaultOptions
  else:
    return defaultOptions[category]
