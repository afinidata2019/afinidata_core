from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from schedule_emails.methods import enviar_correo
from openpyxl import Workbook
import os
from core import settings

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # TODO: query para crear la data
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte"
        ws['A1'] = 'test'
        wb.save(os.path.join(settings.BASE_DIR, 'schedule_emails/test.xlsx'))

        self.stdout.write('its works!')
