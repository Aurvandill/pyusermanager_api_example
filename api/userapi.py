from http import HTTPStatus, client
from sanic import Request, Sanic, text
from sanic.response import json, file

import pyusermanager
from pyusermanager import *
from pyusermanager.Config import *
from pyusermanager.Config.db_providers import *
import pyusermanager.Token as Token

from .return_stuff import *

import re

import os
from binascii import a2b_base64
import imghdr

# app.ctx.lang.

app = Sanic.get_app("api_example")


async def get_users(request):

    success, username = await is_logged_in(request.ctx.token, request.ctx.ip)
    print(username)
    if success:
        return json({"Users": user(app.ctx.cfg).get_users()})
    else:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.not_logged_in, ALERT_TYPE.DANGER), Redirect("/login")
            ),
            HTTPStatus.UNAUTHORIZED,
        )


async def get_user_info(request, username):

    success, found_username = await is_logged_in(request.ctx.token, request.ctx.ip)

    if not success:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.not_logged_in, ALERT_TYPE.DANGER), Redirect("/login")
            ),
            HTTPStatus.UNAUTHORIZED,
        )

    include_email = False

    user_obj = user(app.ctx.cfg, username)
    try:
        if await is_in_group(request.ctx.token, app.ctx.cfg.admin_group_name):
            return json(get_json_from_args(user_obj.info_extended()))

        if found_username == username:
            include_email = True

        return json(user_obj.info(include_email))

    except PyUserExceptions.MissingUserException:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.user_missing, ALERT_TYPE.DANGER), Redirect("/users")
            ),HTTPStatus.BAD_REQUEST
        )


async def get_info_for_header(request):

    logged_in, username = await is_logged_in(request.ctx.token, request.ctx.ip)
    if logged_in:

        found_user = user(app.ctx.cfg, username)
        # check if user is admin!
        if await is_in_group_by_name(username, app.ctx.cfg.admin_group_name):
            return json(
                get_json_from_args(
                    {"admin": True},
                    found_user.info(False),
                    {"registration": app.ctx.cfg.public_registration},
                )
            )

        return json(
            get_json_from_args(
                found_user.info(False),
                {"registration": app.ctx.cfg.public_registration},
            )
        )

    return json(
        {"registration": app.ctx.cfg.public_registration}, HTTPStatus.UNAUTHORIZED
    )


async def update_user_info(request, username):

    logged_in, found_username = await is_logged_in(request.ctx.token, request.ctx.ip)

    if not logged_in:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.not_logged_in, ALERT_TYPE.DANGER), Redirect("/login")
            )
        )

    try:
        this_user = user(app.ctx.cfg, username)
        this_user.info()
    except Exception:
        return json(
            get_json_from_args(Alert(app.ctx.lang.user_missing, ALERT_TYPE.DANGER))
        )

    if not (
        found_username == this_user.username
        or is_in_group_by_name(found_username, app.ctx.cfg.admin_group_name)
    ):
        return json(
            get_json_from_args(Alert(app.ctx.lang.perm_misc_error, ALERT_TYPE.DANGER)), HTTPStatus.UNAUTHORIZED
        )

    json_dict = request.json

    # print(json_dict["img"])
    img_base64 = json_dict.get("img", None)
    password = json_dict.get("password", None)
    passwordconfirm = json_dict.get("passwordconfirm", None)
    email = json_dict.get("email", None)

    if password != passwordconfirm:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.parameter_password_confirm_error, ALERT_TYPE.DANGER)
            )
        )

    try:
        if password is not None:
            this_user.change(password=password)

        if email is not None:
            this_user.change(email=email)

    except:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.parameter_generic_error, ALERT_TYPE.DANGER)
            )
        )

    if img_base64 is not None:
        img_bytes = a2b_base64(img_base64)

        filetype = imghdr.what(None, h=img_bytes)
        if not (filetype == "gif" or filetype == "jpeg" or filetype == "png"):
            return json(
                get_json_from_args(
                    Alert(app.ctx.lang.file_invalid_type, ALERT_TYPE.DANGER), HTTPStatus.BAD_REQUEST
                )
            )

        try:
            # create avatar file
            with open(f"{app.ctx.folders['avatars']}/{username}", "wb") as avatarfile:
                avatarfile.write(img_bytes)

            this_user.change(avatar=username)
        except Exception:
            return json(
                get_json_from_args(
                    Alert(app.ctx.lang.avatar_set_error, ALERT_TYPE.DANGER), HTTPStatus.INTERNAL_SERVER_ERROR
                )
            )

    # change perm stuff if user is admin

    if await is_in_group_by_name(found_username, app.ctx.cfg.admin_group_name):
        perms = json_dict.get("perms", None)

        for perm, add in perms.items():
            print(perm, add)
            Perm(app.ctx.cfg, perm).perm_user(username, add)

    return json(
        get_json_from_args(
            Alert(app.ctx.lang.changes_success), Redirect(f"/user/{username}")
        )
    )


async def delete_user(request, username):
    logged_in, found_username = await is_logged_in(request.ctx.token, request.ctx.ip)

    returnvalue = json(
        get_json_from_args(Alert(app.ctx.lang.user_delete_error, ALERT_TYPE.WARNING))
    )

    if not logged_in:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.not_logged_in, ALERT_TYPE.WARNING), Redirect("/"), HTTPStatus.UNAUTHORIZED
            )
        )

    # allow user to delete himself
    if logged_in and found_username == username:
        user(app.ctx.cfg, username).delete()
        returnvalue = json(
            get_json_from_args(
                {"Logout": True},
                Alert(app.ctx.lang.user_delete_success, ALERT_TYPE.SUCCESS),
                Redirect("/"),
            )
        )
    # allow admins to delete users
    elif await is_in_group(request.ctx.token, app.ctx.cfg.admin_group_name):
        user(app.ctx.cfg, username).delete()
        returnvalue = json(
            get_json_from_args(
                Alert(app.ctx.lang.user_delete_success, ALERT_TYPE.SUCCESS),
                Redirect("/users"),
            )
        )

    return returnvalue


async def login_user(request):
    json_dict = request.json

    logged_in, found_username = await is_logged_in(request.ctx.token, request.ctx.ip)

    if logged_in:
        return json(
            get_json_from_args(
                Redirect("/user/" + found_username),
                Alert(app.ctx.lang.already_logged_in, ALERT_TYPE.INFO),
            ),
            status=HTTPStatus.FORBIDDEN,
        )

    username = json_dict.get("username", None)
    password = json_dict.get("password", None)
    remember_me = json_dict.get("remember_me", False)

    valid_days = 1

    if remember_me:
        valid_days = 365
    try:
        if not login(app.ctx.cfg, username, password):
            return json(
                get_json_from_args(
                    Alert(app.ctx.lang.user_login_error, ALERT_TYPE.DANGER)
                ),
                status=HTTPStatus.UNAUTHORIZED,
            )
    except PyUserExceptions.MissingUserException:
        return json(
            get_json_from_args(Alert(app.ctx.lang.user_missing, ALERT_TYPE.DANGER)),
            status=HTTPStatus.UNAUTHORIZED,
        )

    # create token
    authtoken = Token.Auth(app.ctx.cfg, username=username)
    authtoken.create(request.ctx.ip, valid_days)

    json_ret = get_json_from_args(
        Alert(app.ctx.lang.user_login_success),
        Redirect("/user/" + username),
        {"Login": {"token": authtoken.token}},
    )
    return json(json_ret, HTTPStatus.CREATED)


async def logout_user(request):

    if not await is_logged_in(app.ctx.cfg, request.ctx.token):
        return json(
            get_json_from_args(Alert(app.ctx.lang.not_logged_in), Redirect("/login")),
            status=HTTPStatus.FORBIDDEN,
        )

    authtoken = Token.Auth(app.ctx.cfg, request.ctx.token)
    try:
        authtoken.invalidate(request.ctx.ip)
        return json(
            get_json_from_args(
                {"Logout": True}, Alert(app.ctx.lang.user_logout_success), Redirect("/")
            )
        )
    except ValueError:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.user_logout_error, ALERT_TYPE.WARNING)
            ),
            status=HTTPStatus.BAD_REQUEST,
        )


async def register_user(request):

    if not app.ctx.cfg.public_registration:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.registration_forbidden, ALERT_TYPE.WARNING),
                Redirect("/"),
            ),
            status=HTTPStatus.FORBIDDEN,
        )

    logged_in, found_username = await is_logged_in(request.ctx.token, request.ctx.ip)

    if logged_in:
        return json(
            get_json_from_args(
                Alert(app.ctx.already_logged_in, ALERT_TYPE.WARNING), Redirect("/")
            ),
            status=HTTPStatus.FORBIDDEN,
        )

    json_dict = request.json

    try:
        password = json_dict["password"]
        password_confirm = json_dict["passwordconfirm"]
        username = json_dict["username"]
        email = json_dict["email"]

        matched_username = re.search(r"[a-z,A-Z,_,0-9]*", username)
        print(matched_username)
        if username != matched_username.group():
            return json(
                get_json_from_args(
                    Alert(app.ctx.lang.parameter_username_error, ALERT_TYPE.WARNING)
                ),
                status=HTTPStatus.BAD_REQUEST,
            )

    except Exception as err:
        print(err)
        return json(
            get_json_from_args(Alert(app.ctx.lang.parameter_error, ALERT_TYPE.WARNING)),
            status=HTTPStatus.BAD_REQUEST,
        )

    if password != password_confirm:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.parameter_password_confirm_error, ALERT_TYPE.WARNING)
            ),
            status=HTTPStatus.BAD_REQUEST,
        )
    try:
        await create_user(password, email=email, username=username)
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.user_create_success, ALERT_TYPE.SUCCESS),
                Redirect("/login"),
            ),
            status=HTTPStatus.CREATED,
        )
    except PyUserExceptions.AlreadyExistsException:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.user_create_existing, ALERT_TYPE.DANGER)
            ),
            status=HTTPStatus.BAD_REQUEST,
        )
    except (TypeError, ValueError) as err:
        print(err)
        return json(
            get_json_from_args(Alert(app.ctx.lang.parameter_error, ALERT_TYPE.DANGER)),
            status=HTTPStatus.BAD_REQUEST,
        )


async def create_user(password, username, email):
    user(app.ctx.cfg, username).create(password, email=email)


async def create_by_admin(request):

    logged_in, found_username = await is_logged_in(request.ctx.token, request.ctx.ip)

    if not await is_in_group_by_name(found_username, app.ctx.cfg.admin_group_name):
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.perm_admin_error, ALERT_TYPE.DANGER), Redirect("/")
            ),
            status=HTTPStatus.BAD_REQUEST,
        )
    try:
        json_dict = request.json
        password = json_dict["password"]
        username = json_dict["username"]
        email = json_dict["email"]
        perms = json_dict["perms"]

        await create_user(password, username, email)

        for perm, add in perms.items():
            print(perm, add)
            Perm(app.ctx.cfg, perm).perm_user(username, add)

        return json(
            get_json_from_args(
                Alert(app.ctx.lang.user_create_success, ALERT_TYPE.DANGER)
            ),
            status=HTTPStatus.BAD_REQUEST,
        )

    except Exception as err:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.user_create_error, ALERT_TYPE.DANGER)
            ),
            status=HTTPStatus.BAD_REQUEST,
        )


async def version(request):
    return json({"version": pyusermanager.__version__})


async def get_perms(request):

    success, found_username = await is_logged_in(request.ctx.token, request.ctx.ip)

    if not success:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.not_logged_in, ALERT_TYPE.WARNING),
                Redirect("/login"),
            )
        )

    if not await is_in_group_by_name(found_username, app.ctx.cfg.admin_group_name):
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.perm_admin_error, ALERT_TYPE.WARNING), Redirect("/")
            )
        )

    return json(Perm(app.ctx.cfg, "test").get_all())


async def change_perm(request, add):
    success, found_username = await is_logged_in(request.ctx.token, request.ctx.ip)

    if not success:
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.not_logged_in, ALERT_TYPE.WARNING),
                Redirect("/login"),
            )
        )

    if not await is_in_group_by_name(found_username, app.ctx.cfg.admin_group_name):
        return json(
            get_json_from_args(
                Alert(app.ctx.lang.perm_admin_error, ALERT_TYPE.WARNING), Redirect("/")
            )
        )

    try:
        perm_name = request.json["perm"]
        if len(perm_name) < 4 or perm_name == app.ctx.cfg.admin_group_name:
            raise Exception()
    except Exception:
        return json(
            get_json_from_args(Alert(app.ctx.lang.parameter_error, ALERT_TYPE.DANGER))
        )

    if add:
        if Perm(app.ctx.cfg, perm_name).create():
            return json(get_json_from_args(Alert(app.ctx.lang.perm_create)))
    else:
        if Perm(app.ctx.cfg, perm_name).delete():
            return json(get_json_from_args(app.ctx.lang.perm_delete))

    return json(get_json_from_args(Alert(app.ctx.lang.misc_error, ALERT_TYPE.WARNING)))


async def is_logged_in(token: str, ip="127.0.0.1"):
    """This Function checks if a user is logged in"""
    try:
        auth_token = Token.Auth(app.ctx.cfg, token)
        success = auth_token.verify(ip)
        return success, auth_token.username
    except Exception as err:
        print(err)
        return False, ""


async def is_in_group_by_name(username: str, group: str):
    """checks if a user is in the specified group"""

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
    print(avatarname)
    # print(reee)
    avatarlist = os.listdir(app.ctx.folders["avatars"])

    if avatarname in avatarlist:
        return await file(f"{app.ctx.folders['avatars']}/{avatarname}")
    else:
        return await file(f"{app.ctx.folders['avatars']}/404.png")
