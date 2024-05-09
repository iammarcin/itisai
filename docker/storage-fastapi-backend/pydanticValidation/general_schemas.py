from pydantic import BaseModel, constr
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, validator

class TestModel(BaseModel):
    action: str = ""
    userInput: Dict = {}
    assetInput: Optional[List] = []
    userSettings: Dict = {}
    customerId: int = 1

# 422 error code - if pydantic doesnt like the data
# pydantic data validation for processFile
# taking into account that most data is optional
class CreateVideo(BaseModel):
    imgFiles: Optional[List[str]] = []
    audioFiles: Optional[List[str]] = []
    width: Optional[int] = 1024
    height: Optional[int] = 1024
    resizeImgMethod: Optional[str] = "resize"
    generateZoomVideoMethod: Optional[str] = "noZoom"
    fadeEffectType: Optional[str] = "in"
    fadeEffectLength: Optional[int] = 30
    fadeEffectStartFrame: Optional[int] = 0
    duration: Optional[int] = 5
    customerId: Optional[int] = 1
    params: Optional[Dict] = {}

# pydantic data validation for Image Audio Text Model
# returnTestData - if True - return fake data (this is to test process without calling external APIs)
class MediaModel(BaseModel):
    category: str = ""
    action: str = ""
    userInput: Dict = {}
    assetInput: Optional[List] = []
    userSettings: Dict = {}
    customerId: int = 1
    requestId: Optional[int] = None
    sessionId: Optional[str] = ""
    returnTestData: Optional[bool] = False
    jobId: Optional[str] = ""
    params: Optional[Dict] = {}

# not in use any more
class StreamRequest(BaseModel):
    userInput: dict
    assetInput: Optional[dict] = {}
    category: str
    userSettings: dict

# pydantic data validation for AI Answer
# we want one parameter called prompt and it has to be mandatory
class AIQuestion(BaseModel):
    prompt: constr(min_length=1) = "What is meaning of life?"

# used by Asset Or Suggestion
# category - "image", "video" etc
# action - "generate", "resize" etc
# userInput - what prompt user gave us + some additional parameters (like number of words etc, depending on category)
# assetInput - what assets we have as inputs 
#  this might be list (or list with 1 element) - assets we treat as input
#  it will be often empty - because often we start with nothing (for example we want to generate image from scratch)
# categoryInput - what category of assets we have as inputs
#  this might be useful for workflows
#  to understand how did we get previous assets
# returnTestData - by defualt False
#  little trick - so when its false - we will not call any external services
#  but we will use specified data 
#  so its faster to troubleshoot
# userSettings - settings for user (type of image generator, but also customerId)
# params - additional parameters for specific job (this is optional)
#   for example - jobId for image generator (to check the status)
class GenerateAssetOrSuggestion(BaseModel):
    category: str 
    action: str 
    userInput: Optional[Dict] = {}
    assetInput: Optional[List] = []
    categoryInput: Optional[str] = ""
    returnTestData: Optional[bool] = False
    userSettings: Dict = {}
    params: Optional[Dict] = {}
    customerId: Optional[int] = 1

class ProcessWebUrl(BaseModel):
    url: str

class ProcessYTSubmit(BaseModel):
    url: str
    title: str
    description: str
    requestId: Optional[int] = None
    customerId: Optional[int] = 1