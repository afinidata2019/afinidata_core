from django.views.generic import CreateView
from app import models


class SignUpView(CreateView):
    model = models.User
    fields = ('first_name', 'last_name', 'password', 'identifier')
    template_name = 'app/form.html'
