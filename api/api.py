from sanic import HTTPMethod, Sanic
from sanic.response import json, file

from pyusermanager import *
from pyusermanager.Config import *
from pyusermanager.Config.db_providers import *
import pyusermanager.Token as Token

from .cors import add_cors_headers
from .options import setup_options

from .languages import *


def run(config_paras, debug):

    ##########################################
    #                                        #
    # General Config Setup for Pyusermanager #
    #                                        #
    ##########################################

    if config_paras["db"]["provider"] == "mysql":

        db_cfg = MYSQL_Provider(
            host=config_paras["db"]["host"],
            port=int(config_paras["db"]["port"]),
            user=config_paras["db"]["user"],
            passwd=config_paras["db"]["password"],
            db=config_paras["db"]["db"],
        )
    elif config_paras["db"]["provider"] == "cockroachdb":
        db_cfg = CockroachDB_Provider(
            user=config_paras["db"]["user"],
            password=config_paras["db"]["password"],
            host=config_paras["db"]["host"],
            database=config_paras["db"]["db"],
        )
    elif config_paras["db"]["provider"] == "oracle":
        db_cfg = Oracle_Provider(
            user=config_paras["db"]["user"],
            password=config_paras["db"]["password"],
            dsn=config_paras["db"]["dsn"],
        )
    elif config_paras["db"]["provider"] == "postgresql":
        db_cfg = PostgreSQL_Provider(
            user=config_paras["db"]["user"],
            password=config_paras["db"]["password"],
            host=config_paras["db"]["host"],
            database=config_paras["db"]["db"],
        )
    elif config_paras["db"]["provider"] == "sqlite":
        db_cfg = SQLite_Provider(
            user=config_paras["db"]["user"],
            filename=config_paras["db"]["filename"],
        )

    ad_cfg = AD_Config(
        login = config_paras.getboolean("userapi_LDAP", "Login"),
        address = config_paras["userapi_LDAP"]["address"],
        base_dn = config_paras["userapi_LDAP"]["base_dn"],
        group = config_paras["userapi_LDAP"]["group"],
        suffix = config_paras["userapi_LDAP"]["suffix"],
    )

    cfg = General_Config(
        auto_activate_accounts = config_paras.getboolean(
            "userapi_general", "auto_activate_accounts"
        ),
        admin_group_name = config_paras["userapi_general"]["admin_group_name"],
        public_registration = config_paras.getboolean(
            "userapi_general", "auto_activate_accounts"
        ),
        adcfg = ad_cfg,
        allow_avatars = config_paras.getboolean("userapi_general", "allow_avatars"),
    )
    cfg.bind(db_cfg)

    # creating sanic app
    app = Sanic("api_example")
    # adding cfg to context
    app.ctx.cfg = cfg

    if config_paras["general"]["language"] == "german":
        # add language to context
        app.ctx.lang = LangGer()
    elif config_paras["general"]["language"] == "english":
        # add language to context
        app.ctx.lang = LangEng()
    else:
        # add language to context
        app.ctx.lang = LangEng()

    # add folder paths to app context

    app.ctx.folders = config_paras["folders"]

    from . import userapi

    #########################################
    #                                       #
    #   From here on we assign routes       #
    #                                       #
    #########################################

    app.add_route(userapi.get_users, "/", methods=["POST"])
    app.add_route(userapi.get_info_for_header, "/header", methods=["GET"])

    # login/logout/register routes
    app.add_route(userapi.login_user, "/login", methods=["POST"])
    app.add_route(userapi.logout_user, "/logout", methods=["GET"])
    app.add_route(userapi.register_user, "/register", methods=["POST"])

    # to get versions of stuff
    app.add_route(userapi.version, "/version/pyusermanager", methods=["GET"])

    # Route to get useravatar
    app.add_route(userapi.get_avatar, "/avatar/<avatarname>", methods=["GET"])

    # Methods Regarding Users
    app.add_route(userapi.create_by_admin, "/admin/create", methods=["POST"])
    app.add_route(userapi.get_users, "/users", methods=["GET"])

    @app.route("/perms", methods=["GET", "POST", "DELETE"])
    async def handle_rest_perm(request):

        if request.method == "GET":
            return await userapi.get_perms(request)
        elif request.method == "POST":
            return await userapi.change_perm(request, True)
        elif request.method == "DELETE":
            return await userapi.change_perm(request, False)
        else:
            pass

    @app.route("/user/<username>", methods=["GET", "PUT", "DELETE"])
    async def handle_rest_user(request, username):

        if request.method == "GET":
            return await userapi.get_user_info(request, username)
        elif request.method == "PUT":
            return await userapi.update_user_info(request, username)
        elif request.method == "DELETE":
            return await userapi.delete_user(request, username)
        else:
            pass

    @app.route("/version/api", methods=["GET"])
    def api_version(request):
        return json({"version": "1.0.0"})

    #########################################
    #                                       #
    #   Misc. Setup stuff                   #
    #                                       #
    #########################################

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

    app.run(debug=debug)
