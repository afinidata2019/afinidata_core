from posts.models import Interaction, Feedback
from messenger_users.models import User
from instances.models import PostInteraction
from core.settings import BASE_DIR
from groups.models import Group
import sys
import csv
import os


def run():
    if len(sys.argv) < 4 or len(sys.argv) > 4:
        return None

    group_name = sys.argv[3]
    try:
        group = Group.objects.get(name=group_name)
        with open(os.path.join(BASE_DIR, '%s-core-data.csv' % group_name), 'w', newline='') as csvfile:
            fieldnames = ['user_id', 'user', 'sent', 'open_count', 'open_activities', 'minutes', 'feedback',
                          'core_sent', 'core_session']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for assoc in group.assignationmessengeruser_set.all():
                user = User.objects.get(id=assoc.messenger_user_id)
                sent = Interaction.objects.filter(user_id=user.pk,type__in=['dispatch', 'dispatched'])
                opens = Interaction.objects.filter(user_id=user.pk, type='opened')
                sessions = Interaction.objects.filter(user_id=user.pk, type='session')
                core_sent = set()
                core_session = set()
                read = 0
                for session in sessions:
                    if session.value > 0:
                        read = read + int(session.value)
                feedbacks = Feedback.objects.filter(user_id=user.pk)
                f_total = 0
                for f in feedbacks:
                    f_total = f_total + f.value
                    if f_total > 0:
                        f_total = f_total / feedbacks.count()
                r_open = set(i.post_id for i in opens)
                r_sent = set(i.post_id for i in sent)
                for i in user.get_instances():
                    for inter in i.postinteraction_set.filter(type='dispatched'):
                        core_sent.add(inter.post_id)
                    for inter in i.postinteraction_set.filter(type='session'):
                        core_session.add(inter.post_id)

                data = dict(
                    user_id=user.pk, user=user, sent=len(r_sent), open_count=opens.count(), open_activities=len(r_open),
                    minutes=read, feedback="{:.2f}".format(f_total), core_sent=len(core_sent),
                    core_session=len(core_session)
                )
                writer.writerow(data)
                print(data)
    except Exception as e:
        print(e)
        print('Not possible create file')