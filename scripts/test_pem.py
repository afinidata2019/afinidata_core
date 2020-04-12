import python_jwt as jwt, jwcrypto.jwk as jwk, datetime
from core.settings import BASE_DIR
import pem
import os


def run():
    key = jwk.JWK.generate(kty='RSA', size=2048)
    print('key: ', key)
    priv_pem = key.export_to_pem(private_key=True, password=None)
    print('priv pem: ', priv_pem)
    payload = {'foo': 'bar', 'wup': 90}
    priv_key = jwk.JWK.from_pem(priv_pem)
    print('priv key: ', priv_key)
    token = jwt.generate_jwt(payload, priv_key, 'RS256', datetime.timedelta(minutes=5))
    print('token: ', token)
    header, claims = jwt.verify_jwt(token, priv_key, ['RS256'])
    print(header, claims)
    for k in payload: assert claims[k] == payload[k]

