from posts.models import Interaction
from dateutil.parser import parse
from groups.models import Group
import sys


def run():
    if len(sys.argv) < 6 or len(sys.argv) > 6:
        return None

    init = sys.argv[3]
    finish = sys.argv[4]
    group_name = sys.argv[5]
    users = set()

    date_init = parse(init)
    date_finish = parse(finish)
    group = Group.objects.get(name=group_name)

    interactions = Interaction.objects.filter(created_at__gte=date_init, created_at__lte=date_finish,
                                              type__in=['dispatched', 'opened'],
                                              user_id__in=[u.messenger_user_id for u in group.assignationmessengeruser_set.all()])

    for interaction in interactions:
        users.add(interaction.user_id)

    print(len(users))
