from posts.models import Interaction
from core.settings import BASE_DIR
from groups.models import Group
from dateutil.parser import parse
import sys
import csv
import os


def run():
    if len(sys.argv) < 5 or len(sys.argv) > 5:
        return None

    init = sys.argv[3]
    finish = sys.argv[4]
    users = set()

    date_init = parse(init)
    date_finish = parse(finish)

    interactions = Interaction.objects.filter(created_at__gte=date_init, created_at__lte=date_finish,
                                              type__in=['dispatched', 'opened'])

    for interaction in interactions:
        users.add(interaction.user_id)

    print(len(users))



