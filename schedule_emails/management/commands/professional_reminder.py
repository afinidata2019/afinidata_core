from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from schedule_emails.methods import enviar_correo

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # TODO: Cambiar aqui por el query real
        users = User.objects.all()
        if len(users) > 0:
            for user in users:
                enviar_correo(asunto='Recordatorio de email',template='schedule_emails/professional_reminder.html',recipients=[user.email], data={'user': user})

        self.stdout.write(f"Proceso finalizado!")
