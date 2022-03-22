from sanic import HTTPMethod, Sanic
from sanic.response import json, file

from .cors import add_cors_headers
from .options import setup_options

from sws_webstuff import languages

import importlib


def run(config_paras, debug):

    # creating sanic app
    app = Sanic(config_paras["app_name"])

    try:
        app.ctx.lang = languages.Language[config_paras["language"]].value()
    except Exception as err:
        app.ctx.lang = languages.LangEng()

    # add folder paths to app context

    app.ctx.folders = config_paras["folders"]

    #########################################
    #                                       #
    #   From here on we assign routes       #
    #                                       #
    #########################################

    for mod in config_paras["modules"].keys():
        try:
            api_module = importlib.import_module(mod)
            api_module.configure(config_paras["modules"][mod], app)
            api_module.RegisterRoutes(config_paras["modules"][mod]["route_prefix"], app)
        except:
            ValueError(f"could not load module {mod}")
            return 0

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
        except Exception:
            request.ctx.ip = None

        print(request.method)

    # Add OPTIONS handlers to any route that is missing it
    app.register_listener(setup_options, "before_server_start")

    # Fill in CORS headers
    app.register_middleware(add_cors_headers, "response")

    host = config_paras.get("host", "127.0.0.1")
    port = int(config_paras.get("port", 8080))
    workers = int(config_paras.get("workers", 1))
    ssl = config_paras.get("ssl", None)

    app.run(host=host, port=port, ssl=ssl, debug=debug, workers=workers)
