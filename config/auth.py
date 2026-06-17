from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from typing import Union
import time
import jwt
import os

import repos.user_types.user as user
import repos.user_types.admin as admin
import repos.user_types.driver as driver
import repos.user_types.unverified_driver as unvrf_driver

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
JWT_VALIDITY = os.getenv('JWT_VALIDITY')  # in seconds

VALID_API_KEYS = {os.getenv('API_KEY')}


async def sign_jwt(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "expires": time.time() + float(JWT_VALIDITY),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def verify_jwt(security: HTTPAuthorizationCredentials = Depends(HTTPBearer(scheme_name='Bearer'))) -> str:
    try:
        decoded = jwt.decode(security.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if decoded["expires"] >= time.time():
            return decoded["user_id"]
        else:
            raise HTTPException(status_code=401, detail="Authorization expired")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error verifying JWT: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication")


async def verify_jwt_user(security: HTTPAuthorizationCredentials = Depends(HTTPBearer(scheme_name='Bearer'))) -> str:
    return await jwt_decode_validate(user, security.credentials)


async def verify_jwt_driver(security: HTTPAuthorizationCredentials = Depends(HTTPBearer(scheme_name='Bearer'))) -> str:
    return await jwt_decode_validate(driver, security.credentials)


async def verify_jwt_unvrf_driver(security: HTTPAuthorizationCredentials = Depends(HTTPBearer(scheme_name='Bearer'))) -> str:
    return await jwt_decode_validate(unvrf_driver, security.credentials)


async def verify_jwt_admin(security: HTTPAuthorizationCredentials = Depends(HTTPBearer(scheme_name='Bearer'))) -> str:
    return await jwt_decode_validate(admin, security.credentials)


async def jwt_decode_validate(repo, jwt_token) -> str:
    try:
        decoded = jwt.decode(jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if decoded["expires"] >= time.time():
            uid = decoded["user_id"]
            token = await repo.get_jwt(uid)
            if not token:
                raise HTTPException(401, "Invalid user role")
            if token != jwt_token:
                raise HTTPException(401, "You have been logged out of this device")
            return uid
        else:
            raise HTTPException(status_code=401, detail="Authorization expired")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error verifying JWT: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication")


api_key_header = APIKeyHeader(name="X-API-Key")
def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Missing or invalid API key")


if __name__ == "__main__":
    import asyncio
    test_user_id = "685ca853035ff5a3828eda98"
    test_token = asyncio.run(sign_jwt(test_user_id))
    print(test_token)