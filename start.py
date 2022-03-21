#!/usr/bin/env python3

from api import run

from configobj import ConfigObj
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="kanjiku_backend.py",
        description="a backend for a manga website",
    )

    parser.add_argument(
        "--configfile","-cfg", help="specify a config here", default="./config.ini", type=str
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="should the backend be run in debug mode (default: false)",
        default=False,
    )

    inputvars = parser.parse_args()

    print(inputvars.configfile)

    config = ConfigObj(inputvars.configfile)

    #print(config["general"]["language"])
    run(config,inputvars.debug)

