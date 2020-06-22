from messenger_users.models import User
from posts.models import Interaction
from dateutil.parser import parse
import sys


def run():

    if len(sys.argv) < 5 or len(sys.argv) > 5:
        return None

    init = sys.argv[3]
    finish = sys.argv[4]
    users = set()
    premium_users = set()

    date_init = parse(init)
    date_finish = parse(finish)

    interactions = Interaction.objects.filter(created_at__gte=date_init, created_at__lte=date_finish,
                                              type__in=['dispatched', 'opened'], bot_id=1)

    for interaction in interactions:
        users.add(interaction.user_id)

    for u in users:
        user = User.objects.get(id=u)
        if user.userdata_set.filter(data_key='tipo_de_licencia', data_value='premium').count() > 0:
            premium_users.add(user.pk)

    print(len(premium_users))
