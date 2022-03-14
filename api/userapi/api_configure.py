import pyusermanager
from pyusermanager import *
from pyusermanager.Config import *
from pyusermanager.Config.db_providers import *
from sanic import Sanic

def configure(config_paras):
    

    app = Sanic.get_app("api_example")

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
        groups_prefix = config_paras["userapi_LDAP"]["groups_prefix"],
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

    # adding cfg to context
    app.ctx.cfg = cfg
