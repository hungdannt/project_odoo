import time

from odoo.addons.mail.tools import jwt


def generate_jwt(claims: dict, key: str, ttl: int = None, algorithm: jwt.Algorithm = jwt.Algorithm.HS256) -> str:
    """
    Overwrite the sign function in the odoo base jwt. Allows ttl is None
    A JSON Web Token is a signed pair of JSON objects, turned into base64 strings.

    RFC: https://www.rfc-editor.org/rfc/rfc7519

    :param claims: the payload of the jwt: https://www.rfc-editor.org/rfc/rfc7519#section-4.1
    :param key: base64 string
    :param ttl: the time to live of the token in seconds ('exp' claim)
    :param algorithm: to use to sign the token
    :return: JSON Web Token
    """
    non_padded_key = key.strip("=")
    if ttl:
        claims["exp"] = int(time.time()) + ttl
    return jwt._generate_jwt(claims, non_padded_key, algorithm=algorithm)
