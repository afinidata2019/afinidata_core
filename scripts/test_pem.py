import python_jwt as jwt, jwcrypto.jwk as jwk, datetime
from core.settings import BASE_DIR
import pem
import os


def run():
    key_uri = os.path.join(BASE_DIR, 'afinidata.key')
    key_file = pem.parse_file(key_uri)
    key_string = str(key_file[0]).encode()
    payload = {'foo': 'bar', 'wup': 90}
    priv_key = jwk.JWK.from_pem(key_string)
    token = jwt.generate_jwt(payload, priv_key, 'RS256', datetime.timedelta(minutes=5))
    print('token: ', token)
    header, claims = jwt.verify_jwt(token, priv_key, ['RS256'])
    print(header, claims)
    for k in payload: assert claims[k] == payload[k]

