from messenger_users.models import User
from posts.models import Interaction


def run():
    
    for u in User.objects.all():
        ins = u.get_instances()
        if ins.exists():
            if ins.count() < 2:
                print(u)
                c = ins.first()
                print(c)
                ints = Interaction.objects.filter(user_id=u.pk, type__in=['session', 'dispatched', 'opened'])
                for i in ints:
                    i.instance_id = c.pk
                    i.save()
                    print(i.pk, i.instance_id)

