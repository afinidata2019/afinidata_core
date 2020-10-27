from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView
from user_passwd_reset.forms import PasswordResetForm
from .models import PasswdReset
from django.contrib.auth.models import User

# Create your views here.
class PasswordResetView(TemplateView):
    template_name = 'user_passwd_reset/password_reset.html'

class PasswordResetDoneView(TemplateView):
    template_name = 'user_passwd_reset/password_reset_done.html'

    def post(self, request, *args, **kwargs):
        # TODO: generar token para cambio de constraseña
        # TODO: guardar en base de datos
        # TODO: enviar email
        return render(request, self.template_name)

class PasswordResetConfirmView(TemplateView):
    template_name = 'user_passwd_reset/password_reset_confirm.html'

    def check_token(self, valor):
        valid_token = False
        check = PasswdReset.objects.filter(token=valor, status=0)

        if check.exists():
            valid_token = True

        return valid_token


    def get(self, request, *args, **kwargs):
        form = PasswordResetForm()
        token = kwargs['token']

        return render(request, self.template_name, {'form':form, 'token':token, 'valid_token': self.check_token(token) })

    def post(self, request, *args, **kwargs):
        form = PasswordResetForm(request.POST)
        token = kwargs['token']

        if form.is_valid():
            passwd_reset = PasswdReset.objects.get(token=token)
            passwd_reset.status = 1
            passwd_reset.save()
            user = User.objects.get(pk=passwd_reset.user_id)
            user.set_password(form.cleaned_data.get('password'))
            user.save()

            # TODO: enviar email de "cambiaste tu contraseña"
            return render(request, 'user_passwd_reset/password_reset_complete.html')
        else:
            return render(request, self.template_name, {'form':form, 'token': kwargs['token'], 'valid_token': self.check_token(token)})


