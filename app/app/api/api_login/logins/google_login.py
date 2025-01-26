import json
from typing import Optional
from urllib.parse import urlencode

import requests
from fastapi import Depends, Request, Response
from fastapi.responses import RedirectResponse
from oauthlib.oauth2 import WebApplicationClient
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_login import api_router_login
from app.api.api_v1 import api_router_v1
from app.api.api_login.logins.login_user_origin import login_user_origin
from app.celery_worker.tasks import task_generate_avatar
from app.config.config import settings
from app.database import get_db
from app.models import User
from app.util.rest_util import get_failed_response
from app.util.util import get_user_tokens

google_client = WebApplicationClient(settings.GOOGLE_CLIENT_ID)


def get_google_provider_cfg():
    return requests.get(settings.GOOGLE_DISCOVERY_URL).json()


@api_router_login.get("/google", status_code=200)
async def login_google(
    request: Request,
):
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()

    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    final_redirect_url = str(request.url)
    final_redirect_url = final_redirect_url.replace("http://", "https://", 1)
    request_uri = google_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=str(final_redirect_url) + "/callback",
        scope=["openid", "email", "profile"],
    )
    return RedirectResponse(request_uri)


async def log_user_in(
        userinfo_response,
        db: AsyncSession = Depends(get_db),
):
    users_email = userinfo_response.json()["email"]
    users_name = userinfo_response.json()["given_name"]

    [user, user_created] = await login_user_origin(users_name, users_email, 1, db)

    if user:
        user_token = get_user_tokens(user, 30, 60)
        db.add(user_token)
        await db.commit()
        access_token = user_token.access_token
        refresh_token = user_token.refresh_token

        if user_created:
            db.add(user)
            await db.refresh(user)
            await db.commit()
            _ = task_generate_avatar.delay(user.avatar_filename(), user.id)
        else:
            await db.commit()

        return [True, [access_token, refresh_token, user, user_created]]
    else:
        return [False, [None, None, None, None]]


@api_router_login.get("/google/callback")
async def google_callback(
        code: str,
        request: Request,
        response: Response,
        db: AsyncSession = Depends(get_db),
):
    # Get authorization code Google sent back to you
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay, tokens!
    # Not sure why it reverts to regular http:// but change it back to secure connection
    final_redirect_url = str(request.base_url)
    final_redirect_url = final_redirect_url.replace("http://", "https://", 1)
    final_redirect_url += "login/google/callback"

    authorization_response = str(request.url)
    authorization_response = authorization_response.replace("http://", "https://", 1)

    token_url, headers, body = google_client.prepare_token_request(
        token_endpoint,
        authorization_response=authorization_response,
        redirect_url=final_redirect_url,
        code=code,
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(
            settings.GOOGLE_CLIENT_ID,
            settings.GOOGLE_CLIENT_SECRET,
        ),
    )
    # Parse the tokens!
    google_client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = google_client.add_token(userinfo_endpoint)

    userinfo_response = requests.get(uri, headers=headers, data=body)
    request_base_url = str(request.base_url)

    if not userinfo_response.json().get("email_verified"):
        return get_failed_response("User email not available or not verified by Google.", response)

    [success, [access_token, refresh_token, _]] = await log_user_in(userinfo_response, db)

    if success:
        params = dict()
        params["access_token"] = access_token
        params["refresh_token"] = refresh_token

        url_params = urlencode(params)

        # Send user to the world
        request_base_url = request_base_url.replace("http://", "https://", 1)
        world_url = request_base_url + "butterflyaccess"
        world_url_params = world_url + "?" + url_params
        return RedirectResponse(world_url_params)
    else:
        request_base_url = request_base_url.replace("http://", "https://", 1)
        login_url = request_base_url.replace("/", "/")
        return RedirectResponse(login_url)


class GoogleTokenRequest(BaseModel):
    access_token: str
    is_web: bool


# User the v1 router, so it will have `api/v1.0/` before the path
@api_router_v1.post("/login/google/token", status_code=200)
async def login_google_token(
        google_token_request: GoogleTokenRequest,
        response: Response,
        db: AsyncSession = Depends(get_db),
) -> dict:

    google_access_token = google_token_request.access_token
    is_web = google_token_request.is_web
    userinfo_response = requests.get(
        f"{settings.GOOGLE_ACCESS_TOKEN_URL}?access_token={google_access_token}",
    )

    if userinfo_response.json().get("error", None):
        return get_failed_response("An error occurred", response)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if not userinfo_response.json().get("email_verified"):
        return get_failed_response("User email not available or not verified by Google.", response)

    # We don't use the tokens send with this,
    # because they are only valid for a short period, and we will refresh them later on
    [success, [_, _, user, user_created]] = await log_user_in(userinfo_response, db)

    if success:

        # Log the user in and return all the data we need.
        # This is the same code from `login.py` just copied for simplicity for now.
        # If the platform is 3 we don't need to check anything anymore.
        platform_achievement = False
        platform_achievement_action = user.check_platform_achieved(is_web)
        if platform_achievement_action == 1:
            db.add(user)
        elif platform_achievement_action == 2:
            db.add(user)
            platform_achievement = True

        # Valid login, we refresh the token for this user.
        user_token = get_user_tokens(user)
        db.add(user_token)
        await db.commit()

        if user_created:
            user = user.serialize_no_detail
        else:
            user = user.serialize

        # We don't refresh the user object because we know all we want to know
        login_response = {
            "result": True,
            "message": "user logged in successfully.",
            "access_token": user_token.access_token,
            "refresh_token": user_token.refresh_token,
            "user": user,
            "platform_achievement": False
        }

        if platform_achievement:
            login_response["platform_achievement"] = True

        return login_response
    else:
        return get_failed_response("An error occurred", response)


