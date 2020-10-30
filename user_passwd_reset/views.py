from .models import PasswdReset
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.shortcuts import render, HttpResponse
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from user_passwd_reset.forms import PasswordResetForm, EmailSendForm
import os
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from core import settings

# Create your views here.
def enviar_correo(template, asunto, para, user, token='', request=None):
    image_path = os.path.join(settings.BASE_DIR, 'assets/images/afini_logo.png')
    image_name = 'afini_logo.png'

    context = {'token':token, 'user':user, 'image_name':image_name}
    html_content = render_to_string(template, context, request)
    reply_to = ['no-reply@afinidata.com']

    message = EmailMultiAlternatives(asunto,
    html_content,
    os.getenv('MAIL_USER'),
    to=para,
    reply_to=reply_to)

    message.attach_alternatives = (html_content, "text/html")
    message.content_subtype = "html"
    message.mixed_subtype = 'related'

    with open(image_path, mode='rb') as f:
        image = MIMEImage(f.read())
        message.attach(image)
        image.add_header('Content-ID',f"<{image_name}>")

    message.send()

class PasswordResetView(TemplateView):
    template_name = 'user_passwd_reset/password_reset.html'
    form = EmailSendForm()

    def get_context_data(self, **kwargs):
        context = super(PasswordResetView, self).get_context_data(**kwargs)
        context.update({'form': self.form})
        return context

class PasswordResetDoneView(TemplateView):
    template_name = 'user_passwd_reset/password_reset_done.html'

    def post(self, request, *args, **kwargs):
        token = get_random_string(60)
        email = request.POST['email']

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            passw_reset = PasswdReset(token=token, status=0, user_id=user.id)
            passw_reset.save()

            enviar_correo('user_passwd_reset/email_password_reset.html',asunto="Solicitud de cambio de correo", para=[email], user=user, token=token, request=request)

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

            enviar_correo('user_passwd_reset/email_password_change.html',asunto="Contraseña actualizada", para=[user.email], user=user, request=request)

            return render(request, 'user_passwd_reset/password_reset_complete.html')
        else:
            return render(request, self.template_name, {'form':form, 'token': kwargs['token'], 'valid_token': self.check_token(token)})


