import json
import os

import yaml


class Config:
    """ All configuration details live here """

    _configs = dict()

    @classmethod
    def load(cls, config):
        """ Set a new config database """
        cls._configs = config

    @classmethod
    def find(cls, prop=None, fallback=None):
        """ Find a property """
        return cls._configs.get(prop, fallback)

    @staticmethod
    def strip(env):
        """ Inject config properties from env variables """
        def dict_merge(dct, merge_dct):
            for k, v in merge_dct.items():
                if k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], dict):
                    dict_merge(dct[k], merge_dct[k])
                else:
                    dct[k] = merge_dct[k]

        def strip_yml(path):
            if path and os.path.isfile(path):
                with open(path, encoding='utf-8') as seed:
                    return next(yaml.load_all(seed, Loader=yaml.FullLoader))
            return ''

        env = strip_yml(env)
        dict_merge(env, {k: json.loads(os.getenv(k, '{}')) if isinstance(v, dict) else os.getenv(k, v) for k, v in env.items()})
        return env
