from messenger_users.models import User
from posts.models import Interaction
from core.settings import BASE_DIR
from dateutil.parser import parse
import calendar
import sys
import csv
import os


def run():
    if len(sys.argv) < 5 or len(sys.argv) > 5:
        return None

    month = int(sys.argv[3])
    year = int(sys.argv[4])

    num_days = calendar.monthrange(year, month)[1]
    fieldnames = ['days']
    data = dict(days='')
    for numb in range(1, num_days+1):
        fieldnames.append(f'''{year}-{month}-{numb}''')
        data[f'''{year}-{month}-{numb}'''] = 0

    try:
        with open(os.path.join(BASE_DIR, '%s-%s.csv' % (month, year)), 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for numb in range(1, num_days+1):
                parse_date = parse("%s-%s-%s" % (year, month, numb))
                if not numb == num_days:
                    limit_date = parse("%s-%s-%s" % (year, month, numb + 1))
                else:
                    limit_date = parse("%s-%s-%s 23:59:59" % (year, month, numb))
                total_users = User.objects.filter(created_at__gte=parse_date, created_at__lt=limit_date)
                copy_data = data.copy()
                copy_data[f'''{year}-{month}-{numb}'''] = total_users.count()
                copy_data['days'] = "%s-%s-%s" % (year, month, numb)
                id_users = [u.pk for u in total_users.all()]

                for other_numb in range(numb+1, num_days+1):
                    other_date = parse("%s-%s-%s" % (year, month, other_numb))
                    if not other_numb == num_days:
                        other_limit_date = parse("%s-%s-%s" % (year, month, other_numb + 1))
                    else:
                        other_limit_date = parse("%s-%s-%s 23:59:59" % (year, month, other_numb))
                    interactions = Interaction.objects.filter(created_at__gte=other_date,
                                                              created_at__lt=other_limit_date, user_id__in=id_users,
                                                              type__in=['opened', 'session', 'Start_Session',
                                                                        'dispatched'])
                    day_users = set(i.user_id for i in interactions)
                    copy_data[f'''{year}-{month}-{other_numb}'''] = len(day_users)

                print(copy_data)
                writer.writerow(copy_data)

    except Exception as e:
        print(e)
        print('not possible get data.')
