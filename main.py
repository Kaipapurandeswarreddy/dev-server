from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

from dotenv import load_dotenv
load_dotenv()

import asyncio
import sys
if sys.platform != "win32":
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from config.auth import validate_api_key
from routes import router as api_router
from sockets import router as sockets_router
from routes.webhook import router as webhook_router

fastAPI = FastAPI()
fastAPI.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@fastAPI.middleware("http")
async def add_charset_middleware(request: Request, call_next):
    response = await call_next(request)
    content_type = response.headers.get("content-type")
    if content_type == "application/json":
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response

fastAPI.include_router(api_router, prefix="/api", dependencies=[Depends(validate_api_key)])
fastAPI.include_router(sockets_router, prefix="/ws")
fastAPI.include_router(webhook_router, prefix="/payment")
@fastAPI.get("/terms-conditions")
async def terms_conditions_route():
    return FileResponse("policy/terms_conditions.html")

@fastAPI.get("/privacy-policy")
async def privacy_policy_route():
    return FileResponse("policy/privacy_policy.html")

@fastAPI.get("/cancellation-refunds")
async def cancellation_refunds_route():
    return FileResponse("policy/cancellation_refunds.html")

@fastAPI.get("/shipping-delivery")
async def shipping_delivery_route():
    return FileResponse("policy/shipping_delivery.html")

@fastAPI.get("/contact-us")
async def contact_us_route():
    return FileResponse("policy/contact_us.html")

@fastAPI.get("/account-deletion/request")
async def contact_us_route():
    return FileResponse("policy/account-deletion.html")

@fastAPI.get("/user/app")
async def user_app_download_route(request: Request):
    playstore_url = "https://play.google.com/store/apps/details?id=in.ambigo.user"
    appstore_url = "https://play.google.com/store/apps/details?id=in.ambigo.user"
    user_agent = request.headers.get("user-agent", "").lower()

    if "android" in user_agent:
        return RedirectResponse(playstore_url)
    elif "iphone" in user_agent or "ipad" in user_agent or "ios" in user_agent:
        return RedirectResponse(appstore_url)
    else:
        return RedirectResponse("https://ambigo.in")
    
@fastAPI.get("/driver/app")
async def driver_app_download_route(request: Request):
    playstore_url = "https://play.google.com/store/apps/details?id=in.ambigo.driver"
    user_agent = request.headers.get("user-agent", "").lower()

    if "android" in user_agent:
        return RedirectResponse(playstore_url)
    else:
        return RedirectResponse("https://ambigo.in")

@fastAPI.get("/")
async def index_route():
    return FileResponse("static/index.html")
fastAPI.mount("/", StaticFiles(directory="static"), name="flutter")


@fastAPI.get("/{full_path:path}")
async def fallback(full_path: str):
    return FileResponse("static/index.html")
