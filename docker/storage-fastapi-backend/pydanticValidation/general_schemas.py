from pydantic import BaseModel, constr
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, validator

# 422 error code - if pydantic doesnt like the data

# pydantic data validation for Image Audio Text Model
# returnTestData - if True - return fake data (this is to test process without calling external APIs)
class MediaModel(BaseModel):
    category: str = ""
    action: str = ""
    userInput: Dict = {}
    assetInput: Optional[List] = []
    userSettings: Dict = {}
    customerId: int = 1
    sessionId: Optional[str] = ""


