from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.generic import CreateView
import json
from app import (
    models,
    decorators
)


@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class SignUpView(CreateView):
    model = models.User
    fields = ('first_name', 'last_name', 'password', 'identifier')
    template_name = 'app/form.html'

    def get(self, request, *args, **kwargs):
        return HttpResponse('Unauthorized', status=403)

    def form_valid(self, form):
        user = form.save()
        if user:
            return JsonResponse(dict(status='done', data=dict(user_id=user.pk, user_identifier=user.identifier)))

    def form_invalid(self, form):
        return JsonResponse(dict(status='error', errors=json.loads(form.errors.as_json())))
