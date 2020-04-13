import base64
from django.http import HttpResponse


def check_authorization(view_func):

    def wrap(request, *args, **kwargs):
        auth = None
        try:
            auth = request.META['HTTP_AUTHORIZATION']
        except Exception as e:
            return HttpResponse('<h1>Unauthorized</h1>', status=403)
        encoded_credentials = request.META['HTTP_AUTHORIZATION'].split(' ')[1]
        return view_func(request, *args, **kwargs)

    return wrap
