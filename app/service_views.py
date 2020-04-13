from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from app import (
    models,
    decorators
)


@method_decorator(decorators.check_authorization, name='dispatch')
class SignUpView(CreateView):
    model = models.User
    fields = ('first_name', 'last_name', 'password', 'identifier')
    template_name = 'app/form.html'

    def get(self, request, *args, **kwargs):
        return super(SignUpView, self).get(request, *args, **kwargs)
