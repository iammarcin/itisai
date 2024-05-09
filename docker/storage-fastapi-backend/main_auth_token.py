from fastapi import Request, HTTPException
import logconfig
import config as config
### AUTH
from jose import jwt

logger = logconfig.logger

# authorization via JWT token! so we get the header and check if we can read email from it
async def auth_user_token(request: Request):
    token = request.headers.get("x-access-token")
    if not token:
        logger.info("No token. Probably expired")
        raise HTTPException(status_code=401, detail="You're not authorized to access this resource")
    try:
        payload = jwt.decode(token, config.defaults['JWT_SECRET_KEY'])
        username: str = payload.get("email")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials!!")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
