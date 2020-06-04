import python_jwt as jwt, jwcrypto.jwk as jwk, datetime
from core.settings import BASE_DIR
import pem
import os


def run():
    token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1ODY4MTYzMTIsImZvbyI6ImJhciIsImlhdCI6MTU4NjgxNjI1MiwianRpIjoiV1VJbkhrT01RSFMzSC1LUURIYUpZdyIsIm5iZiI6MTU4NjgxNjI1Miwid3VwIjo5MH0.Ep0hCSDh5FBTxwbPadjh-9P42ePrcTmWgWNv46oyQrSB6jgA9z3kPlZ9NKK7v_MmrfV_Pj1MlUhs1-Umvyk8Cr6gDVb7Mm9mcqDxf3e-sgmYCMxmPPofTPX_b0-faDzL7K_zjdjHmoVFUpsIBONZ8jU8YBXHxu4sKJXIyPNPiYp2kzffnMj8TClUXmCMRK7mrHYgD0RHXwdo9aJT3glmtnxGYdHqkV6ygiasOC5jGSdYKf3jBKzY10vYocOvsMniT25a8Z-CbeFNWriCCDcBOB3Z74speoGreqxBrqVu5h8AJ0EPQ6GJvrRSToNMQMCddEsqNGanU-Rt0wibTZ7hbg'
    key_uri = os.path.join(BASE_DIR, 'afinidata.key')
    key_file = pem.parse_file(key_uri)
    key_string = str(key_file[0]).encode()
    key = jwk.JWK.from_pem(key_string)
    try:
        header, claims = jwt.verify_jwt(token, key, ['RS256'])
        print(header, claims)
    except:
        print('expired')