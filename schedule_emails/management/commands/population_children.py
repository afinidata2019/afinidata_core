from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from schedule_emails.methods import enviar_correo
from openpyxl import Workbook
import os
from core import settings
from openpyxl.styles import Font
from datetime import datetime
from openpyxl.styles import Alignment, Font, Border, Side

class Command(BaseCommand):

    def create_resume(self, wb, sheet_name, header_table, data_total, data_uso, num=0):
        ws = wb.create_sheet(sheet_name,num)

        ws.column_dimensions['A'].width = 32
        ws.column_dimensions['B'].width = 32
        ws.column_dimensions['C'].width = 32
        ws.column_dimensions['D'].width = 32

        thin = Side(border_style="thin", color="333333")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        celda = ws.cell(row=1, column=1, value=f"Afinidata {current_time}")
        celda.font = Font(bold = True, size=12)
        celda = ws.cell(row=2, column=1, value=f"{header_table}")
        celda.font = Font(bold = True, size=12)
        celda = ws.cell(row=3, column=1, value="Sobre uso familias")
        celda.font = Font(bold = True, size=12)

        for row in data_total:
            ws.append(row)

        ws.insert_rows(idx=3, amount=1)
        ws.insert_rows(idx=4, amount=1)

        celda = ws.cell(row=10, column=1, value="Sobre uso profesionales")
        celda.font = Font(bold = True, size=12)

        ws.insert_rows(idx=10, amount=2)

        for row in data_uso:
            ws.append(row)

        for row in ws['B13':'D13']:
            for c in row:
                c.alignment = Alignment(horizontal="center")

        for row in ws['A5':'B9']:
            for cell in row:
                cell.border = border

        for row in ws['A13':'D15']:
            for cell in row:
                cell.border = border

    def handle(self, *args, **kwargs):
        # TODO: query para crear la data

        wb = Workbook()
        std=wb.get_sheet_by_name('Sheet')
        wb.remove_sheet(std)

        # TODO: loop con data real
        data_total = [
            ('total familias',168),
            ('actividades totales', 908),
            ('total de sesiones', 200),
            ('total niños con riesgos identificados', 200),
        ]

        data_uso = [
            ('','ingresaron','pendientes','% ingreso'),
            ('Profesionales que han ingresado',21,9,70.00),
            ('Grupos que han ingresado familias',21,7,33.33),
        ]

        for x in range(0,4):
            if x == 0:
                sheet_name = "Totales generales"
                header_table = "Totales generales"
            else:
                sheet_name = f"title {x}"
                header_table = f"Region {x}"

            self.create_resume(wb=wb,
            num=x,
            data_total=data_total,
            data_uso=data_uso,
            sheet_name=sheet_name,
            header_table=header_table)


        wb.save(os.path.join(settings.BASE_DIR, 'schedule_emails/test.xlsx'))

        self.stdout.write('finish!')
