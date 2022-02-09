from sanic import HTTPMethod, Sanic
from sanic.response import json, file

from pyusermanager import *
from pyusermanager.Config import *
from pyusermanager.Config.db_providers import *
import pyusermanager.Token as Token

from cors import add_cors_headers
from options import setup_options


#configuring pyusermanager lib

db_cfg = MYSQL_Provider(
    host="127.0.0.1", port=3306, user="test", passwd="test1234", db="users"
)
cfg = General_Config(auto_activate_accounts=False,admin_group_name="testperm",public_registration=True)
cfg.bind(db_cfg)


#creating sanic app
app = Sanic("api_example")
#adding cfg to context
app.ctx.cfg = cfg

import userapi

#@app.route('/')
#async def test(request):
#    return json({'hello': 'world'})

app.add_route(userapi.get_users, "/", methods=["POST"])
app.add_route(userapi.get_users, "/users", methods=["GET"])
app.add_route(userapi.get_info_for_header, "/header", methods=["GET"])

@app.route("/user/<username>",methods=["GET","PUT","DELETE"])
async def handle_rest_user(request,username):

    if request.method == "GET":
        return await userapi.get_user_info(request, username)
    elif request.method == "PUT":
        return await userapi.update_user_info(request,username)
    elif request.method == "DELETE":
        return await userapi.delete_user(request,username)
    else:
        pass

app.add_route(userapi.login_user,"/login",methods=["POST"])
app.add_route(userapi.logout_user,"/logout",methods=["GET"])
app.add_route(userapi.register_user,"/register",methods=["POST"])
app.add_route(userapi.version, "/version/pyusermanager", methods=["GET"])
app.add_route(userapi.api_version, "/version/api", methods=["GET"])
app.add_route(userapi.get_avatar, "/avatar/<avatarname>", methods=["GET"])


@app.route("/perms",methods=["GET","POST","DELETE"])
async def handle_rest_perm(request):

    if request.method == "GET":
        return await userapi.get_perms(request)
    elif request.method == "POST":
        return await userapi.change_perm(request,True)
    elif request.method == "DELETE":
        return await userapi.change_perm(request,False)
    else:
        pass

@app.middleware("request")
async def get_info(request):

    try:
        request.ctx.token = request.token
    except Exception:
        request.ctx.token = None

    try:
        request.ctx.ip = request.ip
    except:
        request.ctx.ip = None

    print(request.method)



# Add OPTIONS handlers to any route that is missing it
app.register_listener(setup_options, "before_server_start")

# Fill in CORS headers
app.register_middleware(add_cors_headers, "response")

if __name__ == '__main__':
    app.run(debug=True)