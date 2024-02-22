import os

_ENV_PREFIX = "WAKKALI"


class BaseEnv:
    DEBUG = True


class ENV(BaseEnv):

    @classmethod
    def init_env(cls):
        for env_name, env_value in cls.__dict__.items():
            setattr(
                cls, env_name, os.environ.get(f"{_ENV_PREFIX}_{env_name}", env_value)
            )
