from messenger_users.models import User
from posts.models import Interaction
from core.settings import BASE_DIR
from dateutil.parser import parse
import csv
import sys
import os


def run():

    if len(sys.argv) < 6 or len(sys.argv) > 6:
        return None

    param_users = sys.argv[3]
    init = sys.argv[4]
    finish = sys.argv[5]

    user_ids = param_users.split(',')
    date_init = parse(init)
    date_finish = parse(finish)

    users = User.objects.filter(id__in=user_ids)

    with open(os.path.join(BASE_DIR, 'users repeated activities %s %s.csv' % (init, finish)), 'w', newline='') as csvfile:

        fieldnames = ['ID', 'User', 'Meses', 'Tipo de Licencia', 'Dispatched']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for user in users:
            user_license = None
            child_months = None
            if user.userdata_set.filter(data_key='childMonths').exists():
                print(user.userdata_set.filter(data_key='childMonths').last().data_value)
                child_months = user.userdata_set.filter(data_key='childMonths').last().data_value

            if user.userdata_set.filter(data_key='tipo_de_licencia').exists():
                print(user.userdata_set.filter(data_key='tipo_de_licencia').last().data_value)
                user_license = user.userdata_set.filter(data_key='tipo_de_licencia').last().data_value

            dispatched = [i.post_id for i in Interaction.objects.filter(type='dispatched', user_id=user.pk,
                                                                        created_at__gte=date_init,
                                                                        created_at__lte=date_finish)]
            print(dispatched)
            data = {'ID': user.pk, 'User': user, 'Meses': child_months,'Tipo de Licencia': user_license,
                    'Dispatched': str(dispatched)}
            print(data)
            writer.writerow(data)
