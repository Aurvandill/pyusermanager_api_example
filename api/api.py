from sanic import HTTPMethod, Sanic
from sanic.response import json, file

from .cors import add_cors_headers
from .options import setup_options

from .languages import *

from . import userapi


def run(config_paras, debug):

    
    # creating sanic app
    app = Sanic("api_example")
    

    # setting language
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

    #########################################
    #                                       #
    #   From here on we assign routes       #
    #                                       #
    #########################################
    userapi.configure(config_paras)
    userapi.RegisterRoutes("/")

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
