import python_jwt as jwt, jwcrypto.jwk as jwk, datetime
from core.settings import BASE_DIR
import pem
import os


def generate_key():
    key_uri = os.path.join(BASE_DIR, os.getenv('AUTH_KEY'))
    key_file = pem.parse_file(key_uri)
    key_string = str(key_file[0]).encode()
    key = jwk.JWK.from_pem(key_string)
    return key


def generate_token(json_data):
    key = generate_key()
    token = jwt.generate_jwt(json_data, key, 'RS256', datetime.timedelta(days=1))
    return token
