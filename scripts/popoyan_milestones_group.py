from milestones.models import Milestone
from messenger_users.models import User
from core.settings import BASE_DIR
from groups.models import Group
from instances import models
import csv
import sys
import os


def run():
    group = Group.objects.get(name='Popoyan')
    users = User.objects.filter(id__in=[u.messenger_user_id for u in group.assignationmessengeruser_set.all()])

    with open(os.path.join(BASE_DIR, 'popoyan_children_milestones.csv'), 'w', newline='') as csvfile:
        fieldnames = ['User ID', 'User', 'dispatched']
        for u in users:
            children = u.get_instances()
            if children.exists():
                for c in children:
                    print(c)
                    print(c.response_set.all())
