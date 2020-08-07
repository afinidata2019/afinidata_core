from groups.models import Group
from messenger_users.models import User, UserData
from core.settings import BASE_DIR
from dateutil.parser import parse
from posts.models import Interaction 
import csv
import os


def run():
    group = Group.objects.get(name='Popoyan')
    print(group)

    with open(os.path.join(BASE_DIR, 'popoyan_info.csv'), 'w', newline='') as csvfile:
        fieldnames = ['Mes', 'Usuarios', 'Usuarios_Registrados', 'Instancias', 'Actividades_Enviadas','Usuarios_con_actividad',
                      'Usuarios_Activos', 'IDS']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        all_users = [i.messenger_user_id for i in group.assignationmessengeruser_set.all()]
        param_list = [dict(name='Abril', init='2020-04-01 00:00:00', finish='2020-04-30 23:59:59'),
                      dict(name='Mayo', init='2020-05-01 00:00:00', finish='2020-05-31 23:59:59'),
                      dict(name='Junio', init='2020-06-01 00:00:00', finish='2020-06-30 23:59:59'),
                      dict(name='Julio', init='2020-07-01 00:00:00', finish='2020-07-31 23:59:59'),
                      dict(name='Agosto', init='2020-08-01 00:00:00', finish='2020-08-30 23:59:59')]

        for p in param_list:
            print(p['name'], p['init'], p['finish'])
            data = dict(Mes=p['name'], Usuarios=0, Usuarios_Registrados=0, Instancias=0, Actividades_Enviadas=0,
                        Usuarios_Activos=0, Usuarios_con_actividad=0, IDS=set())
            init = parse(p['init'])
            finish = parse(p['finish'])
            
            assocs = group.assignationmessengeruser_set.filter(created_at__gte=init, created_at__lte=finish)
            month_users = set(x.messenger_user_id for x in assocs)
            registered_users = set(i.user_id for i in UserData.objects.filter(data_key='user_reg',
                                                                              data_value='registered',
                                                                              created__gte=init,
                                                                              created__lte=finish,
                                                                              user_id__in=all_users))
            dispatched_users = set(i.user_id for i in Interaction.objects.filter(created_at__lte=finish, created_at__gte=init,
                                                                                 type='dispatched', user_id__in=all_users ))
            data['Usuarios_con_actividad'] = len(dispatched_users)
            data['Usuarios'] = assocs.count()
            data['Usuarios_Registrados'] = len(registered_users)
            for assoc in assocs:
                user = User.objects.get(id=assoc.messenger_user_id) 
                data['Instancias'] = data['Instancias'] + user.get_instances().count()

            dispatched_list = Interaction.objects.filter(user_id__in=all_users, created_at__gte=init, created_at__lte=finish, type='dispatched')
            active_list = Interaction.objects.filter(user_id__in=all_users, created_at__gte=init, created_at__lte=finish, type__in=['opened', 'Start_Session'])
            active_users = set(it.user_id for it in active_list)
            print(dispatched_list.count())
            print(active_users)
            data['Actividades_Enviadas'] = dispatched_list.count()
            data['Usuarios_Activos'] = len(active_users)
            data['IDS'] = active_users

            writer.writerow(data)
