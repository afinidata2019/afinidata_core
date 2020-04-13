from django.http import HttpResponse
import base64
import os


def check_authorization(view_func):

    def wrap(request, *args, **kwargs):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return HttpResponse('<h1>Unauthorized</h1>', status=403)
        encoded_credentials = request.META['HTTP_AUTHORIZATION'].split(' ')[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
        if decoded_credentials[0] != os.getenv('AUTH_USER') or decoded_credentials[1] != os.getenv('AUTH_PASS'):
            return HttpResponse('<h1>Unauthorized</h1>', status=403)

        return view_func(request, *args, **kwargs)

    return wrap
