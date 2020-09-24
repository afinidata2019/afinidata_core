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
        fieldnames = ['Child', 'Parent', 'Milestones']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for u in users:
            children = u.get_instances()
            if children.exists():
                for c in children:
                    data = dict(Child=c, Parent=u, Milestones=[])
                    milestones = Milestone.objects.filter(
                        id__in=[r.milestone_id for r in c.response_set.filter(response='done')])
                    for m in milestones:
                        data['Milestones'].append(m.name)
                    writer.writerow(data)

