from http import HTTPStatus, client
from sanic import Request, Sanic, text
from sanic.response import json, file

import pyusermanager
from pyusermanager import *
from pyusermanager.Config import *
from pyusermanager.Config.db_providers import *
import pyusermanager.Token as Token

from return_stuff import *

import os

from binascii import a2b_base64
import imghdr

app = Sanic.get_app("api_example")

async def get_users(request):

    success, username = await is_logged_in(request.ctx.token, request.ctx.ip)
    print(username)
    if success:
        return json({"Users":user(app.ctx.cfg).get_users()})
    else:
        return json(get_json_from_args(Alert("not logged in!",ALERT_TYPE.DANGER),Redirect("/login")),HTTPStatus.UNAUTHORIZED)

async def get_user_info(request,username):

    success, found_username = await is_logged_in(request.ctx.token, request.ctx.ip)

    if not success:
        return json(get_json_from_args(Alert("not logged in!",ALERT_TYPE.DANGER),Redirect("/login")),HTTPStatus.UNAUTHORIZED)

    include_email = False

    user_obj = user(app.ctx.cfg,username)
    try:
        if await is_in_group(request.ctx.token,app.ctx.cfg.admin_group_name):
            return json(get_json_from_args(user_obj.info_extended()))

        if found_username == username:
            include_email = True

        return json(user_obj.info(include_email))

    except PyUserExceptions.MissingUserException:
        return json(get_json_from_args(Alert("user does not exist!",ALERT_TYPE.DANGER),Redirect("/users")))
     
async def get_info_for_header(request):

    logged_in, username = await is_logged_in(request.ctx.token, request.ctx.ip)
    if logged_in:

        found_user = user(app.ctx.cfg,username)
        #check if user is admin!
        if await is_in_group_by_name(username, app.ctx.cfg.admin_group_name):
            return json(get_json_from_args({"admin":True},found_user.info(False),{"registration":app.ctx.cfg.public_registration}))

        return json(get_json_from_args(found_user.info(False),{"registration":app.ctx.cfg.public_registration}))
    
    return json({"registration":app.ctx.cfg.public_registration}, HTTPStatus.UNAUTHORIZED)

async def update_user_info(request,username):

    logged_in, found_username = await is_logged_in(request.ctx.token,request.ctx.ip)

    if not logged_in:
      return json(get_json_from_args(Alert("you need to be logged in",ALERT_TYPE.DANGER),Redirect("/login")))  

    try:
        this_user = user(app.ctx.cfg,username)
        this_user.info()
    except Exception:
        return json(get_json_from_args(Alert("User not found!",ALERT_TYPE.DANGER)))

    if not (found_username == this_user.username or is_in_group_by_name(found_username,app.ctx.cfg.admin_group_name)):
        return json(get_json_from_args(Alert("you are not allowed to change other users!",ALERT_TYPE.DANGER)))

    json_dict = request.json

    #print(json_dict["img"])
    img_base64 = json_dict.get("img", None)
    password = json_dict.get("password", None)
    passwordconfirm = json_dict.get("passwordconfirm", None)
    email = json_dict.get("email",None)

    if password != passwordconfirm:
        return json(get_json_from_args(Alert("passwords do not match!",ALERT_TYPE.DANGER)))

    try:
        if password is not None:
            this_user.change(password=password)

        if email is not None:
            this_user.change(email=email)

    except:
        return json(get_json_from_args(Alert("supplied email or password could not be set",ALERT_TYPE.DANGER)))

    if img_base64 is not None:
        img_bytes = a2b_base64(img_base64)


        filetype = imghdr.what(None,h=img_bytes)
        if not(filetype == "gif" or filetype == "jpeg" or filetype == "png"):
            return json(get_json_from_args(Alert("no Valid file given!",ALERT_TYPE.DANGER)))

        try:
            #create avatar file
            with open(f"avatars/{username}","wb") as avatarfile:
                avatarfile.write(img_bytes)

            this_user.change(avatar=username)
        except Exception:
            return json(get_json_from_args(Alert("something went wrong while we wanted to set the avatar!",ALERT_TYPE.DANGER)))

    
    #change perm stuff if user is admin

    if await is_in_group_by_name(found_username,app.ctx.cfg.admin_group_name):
        perms = json_dict.get("perms",None)

        for perm,add in perms.items():
            print(perm,add)
            Perm(app.ctx.cfg,perm).perm_user(username,add)

    return json(get_json_from_args(Alert("Successfull Changes"),Redirect(f"/user/{username}")))

async def delete_user(request,username):
    logged_in, found_username = await is_logged_in(request.ctx.token,request.ctx.ip)

    returnvalue = json(get_json_from_args(Alert("idk what happened",ALERT_TYPE.WARNING)))

    if not logged_in:
        return json(get_json_from_args(Alert("you are not logged in!",ALERT_TYPE.WARNING),Redirect("/")))

    #allow user to delete himself
    if logged_in and found_username == username:
        user(app.ctx.cfg,username).delete()
        returnvalue = json(get_json_from_args({"Logout":True},Alert("User successfully deleted",ALERT_TYPE.SUCCESS),Redirect("/")))
    #allow admins to delete users
    elif await is_in_group(request.ctx.token,app.ctx.cfg.admin_group_name):
        user(app.ctx.cfg,username).delete()
        returnvalue = json(get_json_from_args(Alert("User successfully deleted",ALERT_TYPE.SUCCESS),Redirect("/users")))

    return returnvalue

async def login_user(request):
    json_dict = request.json

    logged_in, found_username = await is_logged_in(request.ctx.token,request.ctx.ip)

    if logged_in:
        return json(get_json_from_args(Redirect("/user/"+found_username),Alert("you are already logged in",ALERT_TYPE.INFO)),status = HTTPStatus.FORBIDDEN)

    username = json_dict.get("username",None)
    password = json_dict.get("password",None)
    remember_me = json_dict.get("remember_me",False)

    valid_days = 1

    if remember_me:
        valid_days = 365
    try:
        if not login(app.ctx.cfg,username,password):
            return json(get_json_from_args(Alert("could not login user",ALERT_TYPE.DANGER)),status = HTTPStatus.UNAUTHORIZED)
    except PyUserExceptions.MissingUserException:
        return json(get_json_from_args(Alert("User does not exist",ALERT_TYPE.DANGER)),status = HTTPStatus.UNAUTHORIZED)

    #create token
    authtoken = Token.Auth(app.ctx.cfg,username=username)
    authtoken.create(request.ctx.ip,valid_days)

    json_ret = get_json_from_args(Alert("login successfull"),Redirect("/user/"+username),{"Login":{"token":authtoken.token}})
    return json(json_ret,HTTPStatus.CREATED)

async def logout_user(request):

    if not await is_logged_in(app.ctx.cfg,request.ctx.token):
        return json(get_json_from_args(Alert("you are not logged in!"),Redirect("/login")),status = HTTPStatus.FORBIDDEN)

    authtoken = Token.Auth(app.ctx.cfg,request.ctx.token)
    try:
        authtoken.invalidate(request.ctx.ip)
        return json(get_json_from_args({"Logout":True},Alert("successfull Logout"),Redirect("/")))
    except ValueError:
        return json(get_json_from_args(Alert("cant logout user from different ip!",ALERT_TYPE.WARNING)),status=HTTPStatus.BAD_REQUEST)

async def register_user(request):


    if not app.ctx.cfg.public_registration:
        return json(get_json_from_args(Alert("registering is prohibited",ALERT_TYPE.WARNING),Redirect("/")),status = HTTPStatus.FORBIDDEN)

    logged_in, found_username = await is_logged_in(request.ctx.token,request.ctx.ip)
    
    if logged_in:
        return json(get_json_from_args(Alert("you are logged in already",ALERT_TYPE.WARNING),Redirect("/")),status = HTTPStatus.FORBIDDEN)

    json_dict = request.json

    try:
        password = json_dict["password"]
        password_confirm = json_dict["passwordconfirm"]
        username = json_dict["username"]
        email = json_dict["email"]

    except Exception as err:
        return json(get_json_from_args(Alert("Not enough parameters supplied",ALERT_TYPE.WARNING)),status=HTTPStatus.BAD_REQUEST)

    if password != password_confirm:
        return json(get_json_from_args(Alert("passwords do not match",ALERT_TYPE.WARNING)),status=HTTPStatus.BAD_REQUEST)
    try:
        await create_user(password,email,username)
        return json(get_json_from_args(Alert("user successfully created",ALERT_TYPE.SUCCESS),Redirect("/login")),status=HTTPStatus.CREATED)
    except PyUserExceptions.AlreadyExistsException:
        return json(get_json_from_args(Alert("user already exists",ALERT_TYPE.DANGER)),status=HTTPStatus.BAD_REQUEST)
    except (TypeError, ValueError):
        return json(get_json_from_args(Alert("supplied Data is not Valid!",ALERT_TYPE.DANGER)),status=HTTPStatus.BAD_REQUEST)


async def create_user(password,username,email):
    user(app.ctx.cfg,username).create(password,email=email)

async def create_by_admin(request):

    logged_in, found_username = await is_logged_in(request.ctx.token,request.ctx.ip)

    if not await is_in_group_by_name(found_username,app.ctx.cfg.admin_group_name):
        return json(get_json_from_args(Alert("you must be an admin to do this!",ALERT_TYPE.DANGER), Redirect("/")),status=HTTPStatus.BAD_REQUEST)
    try:
        json_dict = request.json
        password = json_dict["password"]
        username = json_dict["username"]
        email = json_dict["email"]
        perms = json_dict["perms"]

        await create_user(password,username,email)

        for perm,add in perms.items():
            print(perm,add)
            Perm(app.ctx.cfg,perm).perm_user(username,add)

        return json(get_json_from_args(Alert("successfully created User",ALERT_TYPE.DANGER)),status=HTTPStatus.BAD_REQUEST)

    except Exception as err:
        return json(get_json_from_args(Alert("could not create User!",ALERT_TYPE.DANGER)),status=HTTPStatus.BAD_REQUEST)


async def version(request):
    return json({"version":pyusermanager.__version__})

async def api_version(request):
    return json({"version":"1.0.0"})

async def get_perms(request):

    success, found_username = await is_logged_in(request.ctx.token,request.ctx.ip)

    if not success:
        return json(get_json_from_args(Alert("you need to be logged in",ALERT_TYPE.WARNING),Redirect("/login")))

    if not await is_in_group_by_name(found_username, app.ctx.cfg.admin_group_name):
        return json(get_json_from_args(Alert("you need to be an admin to see this",ALERT_TYPE.WARNING),Redirect("/")))

    return json(Perm(app.ctx.cfg,"test").get_all())

async def change_perm(request,add):
    success, found_username = await is_logged_in(request.ctx.token,request.ctx.ip)

    if not success:
        return json(get_json_from_args(Alert("you need to be logged in",ALERT_TYPE.WARNING),Redirect("/login")))

    if not await is_in_group_by_name(found_username, app.ctx.cfg.admin_group_name):
        return json(get_json_from_args(Alert("you need to be an admin to see this",ALERT_TYPE.WARNING),Redirect("/")))

    try:
        perm_name = request.json["perm"]
        if len(perm_name) < 4 or perm_name == app.ctx.cfg.admin_group_name:
            raise Exception()
    except Exception:
        return json(get_json_from_args(Alert("No Valid Perm submitted",ALERT_TYPE.DANGER)))

    if add:
        if Perm(app.ctx.cfg,perm_name).create():
            return json(get_json_from_args(Alert("Perm created")))
    else:
        if Perm(app.ctx.cfg,perm_name).delete():
            return json(get_json_from_args(Alert("Perm Deleted")))

    return json(get_json_from_args(Alert("could not do that",ALERT_TYPE.WARNING)))

async def is_logged_in(token: str,ip="127.0.0.1"):
    """This Function checks if a user is logged in"""
    try:
        auth_token = Token.Auth(app.ctx.cfg,token)
        success = auth_token.verify(ip)
        return success, auth_token.username
    except Exception as err:
        print(err)
        return False , ""

async def is_in_group_by_name(username: str, group: str):
    """checks if a user is in the specified group"""

    try:
        found_user = user(app.ctx.cfg,username)
        userinfo = found_user.info_extended()
        if group in userinfo["perms"]:
            return True
    except Exception as err:
        pass
    
    return False

async def is_in_group(token: str, group: str):
    """checks if a user is in the specified group"""

    try:
        auth_token = Token.Auth(app.ctx.cfg,token)
        auth_token.get_user()
        user_dict = user(app.ctx.cfg,auth_token.username).info_extended()
        print(user_dict)
        if group in user_dict["perms"]:
            return True
    except Exception as err:
        return False
    
    return False

async def get_avatar(request,avatarname):
    print(avatarname)
    #print(reee)
    avatarlist = os.listdir("avatars")

    if avatarname in avatarlist:
        return await file(f"avatars/{avatarname}")
    else:
        return await file(f"avatars/404.png")