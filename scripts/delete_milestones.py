from milestones.models import Milestone


def run():
    for m in Milestone.objects.filter(value__lte=35):
        if not m.second_code or m.second_code[0:2] != 'LF':
            print(m.pk, 'for delete')
            m.delete()
