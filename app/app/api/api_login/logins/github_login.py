from typing import Optional
from urllib.parse import urlencode

import requests
from fastapi import Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_login import api_router_login
from app.api.api_login.logins.login_bro_origin import login_bro_origin
from app.celery_worker.tasks import task_generate_avatar
from app.config.config import settings
from app.database import get_db
from app.models import Bro
from app.util.util import get_bro_tokens


@api_router_login.get("/github", status_code=200)
async def login_github(
    request: Request,
):
    # Find out what URL to hit for GitHub login
    base_url = settings.GITHUB_AUTHORIZE
    params = dict()
    params["client_id"] = settings.GITHUB_CLIENT_ID

    url_params = urlencode(params)
    github_url = base_url + "/?" + url_params
    return RedirectResponse(github_url, status_code=status.HTTP_302_FOUND)


@api_router_login.get("/github/callback")
async def github_callback(
    code: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Get authorization code GitHub sent back to you
    access_base_url = settings.GITHUB_ACCESS
    params = dict()
    params["client_id"] = settings.GITHUB_CLIENT_ID
    params["client_secret"] = settings.GITHUB_CLIENT_SECRET
    params["code"] = code

    url_params = urlencode(params)
    github_post_url = access_base_url + "/?" + url_params

    headers = {
        "Accept": "application/json",
    }
    token_response = requests.post(github_post_url, headers=headers)

    github_response_json = token_response.json()

    headers_authorization = {
        "Accept": "application/json",
        "Authorization": "Bearer %s" % github_response_json["access_token"],
    }
    authorization_url = settings.GITHUB_USER

    authorization_response = requests.get(authorization_url, headers=headers_authorization)

    github_bro = authorization_response.json()

    bro_name = github_bro["login"]
    bro_email = github_bro["email"]

    [bro, bro_created] = await login_bro_origin(bro_name, bro_email, 2, db)

    if bro:
        bro_token = get_bro_tokens(bro, 30, 60)
        db.add(bro_token)
        await db.commit()
        access_token = bro_token.access_token
        refresh_token = bro_token.refresh_token

        db.add(bro)
        await db.commit()
        await db.refresh(bro)

        if bro_created:
            db.add(bro)
            await db.refresh(bro)
            await db.commit()
            _ = task_generate_avatar.delay(bro.avatar_filename(), bro.id)
        else:
            await db.commit()

        params = dict()
        params["access_token"] = access_token
        params["refresh_token"] = refresh_token
        url_params = urlencode(params)

        # Send bro to the world
        request_base_url = str(request.base_url)
        request_base_url = request_base_url.replace("http://", "https://", 1)
        world_url = request_base_url + "broaccess"
        world_url_params = world_url + "?" + url_params
        return RedirectResponse(world_url_params)
    else:
        request_base_url = str(request.base_url)
        request_base_url = request_base_url.replace("http://", "https://", 1)
        login_url = request_base_url.replace("/login/github/callback", "/")
        return RedirectResponse(login_url)
