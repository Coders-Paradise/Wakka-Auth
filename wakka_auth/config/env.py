import os

_ENV_PREFIX = "WAKKA"


class BaseEnv:
    DEBUG = "True"
    DB_NAME = "database"
    DB_USER = "user"
    DB_PASS = "pass"
    DB_HOST = "localhost"
    DB_PORT = "3306"

    SECRET_KEY = "secret_key"
    JWT_PRIVATE_KEY = "jwt_private_key"
    JWT_PUBLIC_KEY = "jwt_public_key"

    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_FROM = "example@gmail.com"
    EMAIL_HOST_USER = "example@gmail.com"
    EMAIL_HOST_PASSWORD = "pass"

    SINGLE_APP = "false"
    APP_NAME = "app"


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
