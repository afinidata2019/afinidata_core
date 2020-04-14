from django.contrib.auth.hashers import check_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.generic import CreateView, View
from instances.models import Instance
import json
from app import (
    decorators,
    utilities,
    models,
    forms,
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


@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Unauthorized', status=403)

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(status='error', errors=json.loads(form.errors.as_json())))

        checker = check_password(form.cleaned_data['password'], form.cleaned_data['identifier'].password)
        if not checker:
            return JsonResponse(dict(status='error', errors=dict(
                password=[dict(message='Invalid Password', code='required')]
            )))
        token = utilities.generate_token(dict(user_id=form.cleaned_data['identifier'].pk))
        return JsonResponse(dict(status='done', data=dict(
            first_name=form.cleaned_data['identifier'].first_name,
            last_name=form.cleaned_data['identifier'].last_name,
            user_id=form.cleaned_data['identifier'].pk,
            token=token
        )))


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(decorators.verify_token, name='dispatch')
class CreateInstanceView(CreateView):
    model = Instance
    fields = ('name', 'entity')

    def get(self, request, *args, **kwargs):
        return HttpResponse('Unauthorized', status=403)

