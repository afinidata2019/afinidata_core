from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class PasswordResetView(TemplateView):
    template_name = 'user_passwd_reset/password_reset.html'

class PasswordResetDoneView(TemplateView):
    template_name = 'user_passwd_reset/password_reset_done.html'

    def post(self, request, *args, **kwargs):
        # TODO: generar token para cambio de constraseña
        # TODO: guardar en base de datos
        # TODO: enviar email
        return render(request, self.template_name, {'data': "test"})

class PasswordResetConfirmView(TemplateView):
    template_name = 'user_passwd_reset/password_reset_confirm.html'


class PasswordResetCompleteView(TemplateView):
    # TODO: comprobar token
    # TODO: mostrar formulario de cambio constraseña
    # TODO: validar nueva contraseña y actualizar en base de datos.
    # TODO: mensaje de confirmacion de contraseña actualizada.
    template_name = 'user_passwd_reset/password_reset_complete.html'

    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, {'data': "test"})

