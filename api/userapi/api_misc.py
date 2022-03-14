import os
from sanic import Sanic
from sanic.response import json, file

import pyusermanager
from pyusermanager import *
from pyusermanager.Config import *
from pyusermanager.Config.db_providers import *
import pyusermanager.Token as Token

async def version(request):
    return json({"version": pyusermanager.__version__})


async def is_logged_in(token: str, ip="127.0.0.1"):
    """This Function checks if a user is logged in"""
    app = Sanic.get_app("api_example")
    try:
        auth_token = Token.Auth(app.ctx.cfg, token)
        success = auth_token.verify(ip)
        return success, auth_token.username
    except Exception as err:
        print(err)
        return False, ""

async def is_in_group_by_name(username: str, group: str):
    """checks if a user is in the specified group"""
    app = Sanic.get_app("api_example")

    try:
        found_user = user(app.ctx.cfg, username)
        userinfo = found_user.info_extended()
        if group in userinfo["perms"]:
            return True
    except Exception as err:
        pass

    return False

async def is_in_group(token: str, group: str):
    """checks if a user is in the specified group"""
    app = Sanic.get_app("api_example")

    try:
        auth_token = Token.Auth(app.ctx.cfg, token)
        auth_token.get_user()
        user_dict = user(app.ctx.cfg, auth_token.username).info_extended()
        print(user_dict)
        if group in user_dict["perms"]:
            return True
    except Exception as err:
        return False

    return False

async def get_avatar(request, avatarname):
    app = Sanic.get_app("api_example")
    
    avatarlist = os.listdir(app.ctx.folders["avatars"])

    if avatarname in avatarlist:
        return await file(f"{app.ctx.folders['avatars']}/{avatarname}")
    else:
        return await file(f"{app.ctx.folders['avatars']}/404.png")

async def create_user(password, username, email):
    app = Sanic.get_app("api_example")
    user(app.ctx.cfg, username).create(password, email=email)

