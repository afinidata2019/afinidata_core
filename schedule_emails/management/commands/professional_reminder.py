from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from groups.models import RoleGroupUser
from schedule_emails.methods import enviar_correo
from django.db import connection

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        cursor = connection.cursor()
        query = """
        select distinct(email), auth_user.id, username, first_name, last_name
        from auth_user
            inner join groups_rolegroupuser
                on groups_rolegroupuser.user_id = auth_user.id
            inner join groups_group
                on groups_rolegroupuser.group_id = groups_group.id
            inner join groups_group as grupo_padre
                on groups_group.parent_id = grupo_padre.id
            left join groups_assignationmessengeruser
                on groups_assignationmessengeruser.group_id = groups_group.id
        where grupo_padre.parent_id = 38
        and email is not null
        and email != ''
        """
        cursor.execute(query)
        users = cursor.fetchall()
        if len(users) > 0:
            for user in users:
                    cursor = connection.cursor()
                    # total niños por grupo del usuario actual
                    query = """
                        select count(1), group_id from instances_instanceassociationuser t1
                        inner join groups_rolegroupuser t2 on (t2.user_id = t1.user_id)
                        where group_id in(select group_id from groups_rolegroupuser where user_id = %s)
                        group by 2;
                    """

                    cursor.execute(query, [user[1]])

                    result = cursor.fetchone()

                    if result:
                        total_children = result[0]
                    else:
                        total_children = 0

                    group = RoleGroupUser.objects.get(user_id=user[1])

                    # link de referido
                    cursor.execute("""
                    select url, code
                    from bots_bot t1
                    inner join groups_botassignation t2 on (t2.bot_id = t1.id)
                    inner join groups_code t3 on(t2.group_id = t3.group_id)
                    where user_id = %s
                    order by t1.id desc limit 1;
                    """,[user[1]])

                    result = cursor.fetchone()

                    if result:
                        url_referido = result[0] + "?code=+" + result[1]
                    else:
                        url_referido = "#"

                    # enviar_correo(
                    #     asunto='Recordatorio de email',
                    #     template='schedule_emails/professional_reminder.html',
                    #     recipients=[user[0]],
                    #     data={
                    #         'user': {'username':user[2],'first_name': user[3], 'last_name':user[4]},
                    #         'total_children':total_children,
                    #         'group': group.pk,
                    #         'url_referido': url_referido
                    #     }
                    # )

                    enviar_correo(
                        asunto='Recordatorio de email',
                        template='schedule_emails/professional_reminder.html',
                        recipients=['alejandro.reyna@afinidata.com','lgodoy@afinidata.com','ac@afindata.com'],
                        data={
                            'user': {'username':user[2],'first_name': user[3], 'last_name':user[4]},
                            'total_children':total_children,
                            'group': group.pk,
                            'url_referido': url_referido
                        }
                    )
