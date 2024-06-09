from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logconfig
import config as config
### AUTH
from jose import jwt

logger = logconfig.logger

# TEMP solution, far from prod ready
# token generated via generate-jwt-token.py
# and added to options in app manually
# valid for 1 year

# authorization via JWT token! so we get the header and check if we can read email from it
async def auth_user_token(request: Request):
    #token = request.headers.get("x-access-token") # react
    # from android we receive
    # .addHeader("Authorization", "Bearer $authToken")
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        logger.info("No Authorization header. Probably expired")
        raise HTTPException(status_code=401, detail="You're not authorized to access this resource")

    token = auth_header.split(" ")[1] if " " in auth_header else None
    if not token:
        logger.info("No token found in Authorization header")
        raise HTTPException(status_code=401, detail="You're not authorized to access this resource")

    try:
        payload = jwt.decode(token, config.defaults['JWT_SECRET_KEY'], algorithms='HS256')
        username: str = payload.get("email")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials!!")
            #return JSONResponse(content={"success": False, "code": 401, "message": {"status": "fail", "result": "Invalid authentication credentials!!"}}, status_code=401)
    except jwt.JWTError as e:
        logger.error(e)
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        #return JSONResponse(content={"success": False, "code": 401, "message": {"status": "fail", "result": "Invalid authentication credentials!!"}}, status_code=401)
