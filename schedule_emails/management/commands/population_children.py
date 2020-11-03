import os
from core import settings
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font
from django.db import connection
from django.contrib.auth.models import User
from schedule_emails.methods import enviar_correo
from openpyxl.styles import Alignment, Font, Border, Side
from django.core.management.base import BaseCommand, CommandError
from openpyxl.utils import get_column_letter

class Command(BaseCommand):

    def create_report(self, wb):
        heading = ('nro','región','distrito','eess','nro de niño de 0 a 24 meses','nombre','apellido paterno', 'apellido materno', 'dni','celular','total de familias','ingreso de profesional en la ultima semana')
        ws = wb.create_sheet('Reporte')
        ws.append(heading)

        border = Border(
            left=Side(border_style='thin', color='000000'),
            right=Side(border_style='thin', color='000000'),
            top=Side(border_style='thin', color='000000'),
            bottom=Side(border_style='thin', color='000000')
        )

        cursor = connection.cursor()

        # TODO: carmbiar por el query real

        query = """
            select * from auth_user
        """
        cursor.execute(query)
        result = cursor.fetchall()

        if len(result) > 0:
            # TODO: loop de la data
            pass

            for row in ws.iter_rows():
                for cell in row:
                    cell.border = border

            for i, col in enumerate(ws.columns):
                ws.column_dimensions[get_column_letter(i+1)].width = 25


    def handle(self, *args, **kwargs):

        archivo = os.path.join(settings.BASE_DIR, 'schedule_emails/reporte.xlsx')
        wb = Workbook()
        std=wb.get_sheet_by_name('Sheet')
        wb.remove_sheet(std)
        ws = wb.create_sheet('Consolidado')

        cursor = connection.cursor()
        query = """
        select grupo_padre.name as 'Región',
            groups_group.name as 'Grupo',
            count(distinct groups_assignationmessengeruser.user_id) as 'familias',
            count(distinct posts_interaction.id) as 'actividades',
            count(distinct user_sessions_interaction.id) as 'sesiones',
            count(distinct case when auth_user.last_login is null
                    then NULL else auth_user.id end) as 'Ingresaron',
            count(distinct case when auth_user.last_login is null
                    then auth_user.id else NULL end) as 'Pendientes'
        from groups_group
            left join groups_group as grupo_padre
                on groups_group.parent_id = grupo_padre.id
            left join groups_assignationmessengeruser
                on groups_assignationmessengeruser.group_id = groups_group.id
            left join user_sessions_interaction
                on user_sessions_interaction.user_id = groups_assignationmessengeruser.user_id
                and user_sessions_interaction.`type` = 'session_init'
            left join posts_interaction
                on posts_interaction.user_id = groups_assignationmessengeruser.user_id
                and posts_interaction.`type` = 'dispatched'
            left join groups_rolegroupuser
                on groups_rolegroupuser.group_id = groups_group.id
            left join auth_user
                on groups_rolegroupuser.user_id = auth_user.id
        group by grupo_padre.id
        order by grupo_padre.name asc, groups_group.name asc
        """
        cursor.execute(query)
        result = cursor.fetchall()

        # TODO: calcular ingresaron, pendientes y porcentaje
        if len(result) > 0:
            totales = [
                ('',),
                ('TOTALES GENERALES',),
                ('',),
                ('SOBRE USO DE FAMILIAS',),
                ('Total familias',sum(row[2] for row in result)),
                ('Actividades totales', sum(row[3] for row in result)),
                ('Total de sesiones', sum(row[4] for row in result)),
                ('Total niños con riesgos identificados', 0),
                ('',),
                ('SOBRE USO DE PROFESIONALES',),
                ('','Ingresaron','Pendientes','% Ingreso'),
                ('Profesionales que han ingresado',21,9,70.00),
                ('Grupos que han ingresado familias',21,7,33.33),
                ('',),
                ('',)
            ]

            for row in totales:
                ws.append(row)

            for i,row in enumerate(result):

                ws.cell(row=ws.max_row+1, column=1, value="REGIÓN {0}".format(row[0]))

                # TODO: calcular ingresaron, pendientes y porcentaje
                data_total = [
                    ('',),
                    ('SOBRE USO DE FAMILIAS',),
                    ('Total familias',row[2]),
                    ('Actividades totales', row[3]),
                    ('Total de sesiones', row[4]),
                    ('Total niños con riesgos identificados', 0),
                    ('',),
                    ('',),
                    ('SOBRE USO DE PROFESIONALES',),
                    ('','Ingresaron','Pendientes','% Ingreso'),
                    ('Profesionales que han ingresado',21,9,70.00),
                    ('Grupos que han ingresado familias',21,7,33.33),
                    ('',),
                    ('',)
                ]

                for row in data_total:
                    ws.append(row)

            for i, col in enumerate(ws.columns):
                ws.column_dimensions[get_column_letter(i+1)].width = 35

            self.create_report(wb)

            wb.save(archivo)

            #TODO: consultar usuarios, enviar por correo con archivo adjunto.
            enviar_correo(asunto='Población de niños',template='schedule_emails/population_children.html',data=None, recipients=['correo@prueba.com'], attachment_file=archivo)

