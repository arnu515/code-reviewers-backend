from redis import StrictRedis
from os import getenv as env

from .. import jwt

rd = StrictRedis(host=env("REDIS_HOST", "localhost"), port=int(env("REDIS_PORT", "6379")), db=int(env("REDIS_DB", "0")),
                 password=env("REDIS_PASS", ""), decode_responses=True)


@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token: dict):
    return rd.get(decrypted_token["jti"]) != 'false'


def revoke_token(jti: str):
    rd.set(jti, 'true', int(86400 * 1.2))


def store_token(jti: str):
    rd.set(jti, 'false', int(86400 * 1.2))
