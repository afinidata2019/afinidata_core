from messenger_users.models import User
from posts.models import Interaction
from core.settings import BASE_DIR
from dateutil.parser import parse
import csv
import sys
import os


def run():
    if len(sys.argv) < 5 or len(sys.argv) > 5:
        return None

    init = sys.argv[3]
    finish = sys.argv[4]

    date_init = parse(init)
    date_finish = parse(finish)

    interactions = Interaction.objects.filter(created_at__gte=date_init, created_at__lte=date_finish,
                                              type='dispatched', bot_id=1)

    filter_users = set(i.user_id for i in interactions)

    with open(os.path.join(BASE_DIR, 'users-dispatched-data-%s-%s.csv' % (init, finish)), 'w', newline='') as csvfile:
        fieldnames = ['User ID', 'User', 'dispatched']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for f in filter_users:
            try:
                u = User.objects.get(id=f)
                data = {'User ID': u.pk, 'User': u, 'dispatched': interactions.filter(user_id=u.pk).count()}
                print(data)
                writer.writerow(data)
            except Exception as e:
                print(e)
                pass

