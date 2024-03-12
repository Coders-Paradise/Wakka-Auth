import os

_ENV_PREFIX = "WAKKA"


class BaseEnv:
    DEBUG = "True"
    SECRET_KEY = "secret_key"
    DB_NAME = "database"
    DB_USER = "user"
    DB_PASS = "pass"
    DB_HOST = "localhost"
    DB_PORT = "3306"
    SERVER_API_KEY = "server_api_key"


class ENV(BaseEnv):

    @classmethod
    def init_env(cls):
        for env_var in dir(cls):
            if env_var.isupper():
                setattr(
                    cls,
                    env_var,
                    os.getenv(f"{_ENV_PREFIX}_{env_var}", getattr(cls, env_var)),
                )
