from messenger_users.models import User, ChildData, Child
from instances.models import Instance, Response
from milestones.models import Milestone


def run():

    count = 0

    for instance in Instance.objects.all():

        assoc = instance.instanceassociationuser_set.all()

        if assoc.count() > 0:

            parents = User.objects.filter(id=assoc.last().user_id)
            if parents.count() > 0:
                parent = parents.last()

                child_data = ChildData.objects \
                    .filter(child__parent_user_id=parent.pk,
                            data_key__in=[milestone.second_code for milestone in Milestone.objects.all()],
                            data_value__in=['Completado', 'done', 'Si lo hace'])

                parent_data = parent.userdata_set.filter(
                    data_key__in=[milestone.second_code for milestone in Milestone.objects.all()],
                    data_value__in=['Completado', 'done', 'Si lo hace'])

                if child_data.count() > 0 or parent_data.count() > 0:
                    print(instance.pk, parent.pk, parent.first_name)
                    print('positives: ', 'child: ', child_data.count(), 'parent: ', parent_data.count())

                negative_child_data = ChildData.objects \
                    .filter(child__parent_user=parent,
                            data_key__in=[milestone.second_code for milestone in Milestone.objects.all()],
                            data_value__in=['Todavía no'])

                negative_parent_data = parent.userdata_set.filter(
                    data_key__in=[milestone.second_code for milestone in Milestone.objects.all()],
                    data_value__in=['Todavía no'])

                if negative_child_data.count() > 0 or negative_parent_data.count() > 0:
                    print(instance.pk, parent.pk, parent.first_name)
                    print('negatives: ', 'child: ', negative_child_data.count(), 'parent: ', negative_parent_data.count())

                if negative_child_data.count() > 0:
                    for data in negative_child_data:
                        response = Response.objects.create(instance=instance,
                                                           milestone=Milestone.objects.get(second_code=data.data_key),
                                                           response='failed',
                                                           created_at=data.timestamp)
                        print(instance.pk, response.milestone, response)
                        count = count + 1

                if negative_parent_data.count() > 0:
                    for data in negative_parent_data:
                        response = Response.objects.create(instance=instance,
                                                           milestone=Milestone.objects.get(second_code=data.data_key),
                                                           response='failed',
                                                           created_at=data.created)
                        print(instance.pk, response.milestone, response)
                        count = count + 1

                if parent_data.count() > 0:
                    for data in parent_data:
                        if instance.response_set.filter(milestone__second_code=data.data_key, response='done').count() < 1:
                            response = Response.objects.create(instance=instance,
                                                               milestone=Milestone.objects.get(second_code=data.data_key),
                                                               response='done',
                                                               created_at=data.created)
                            print(instance.pk, response.milestone, response.response)
                            count = count + 1

                if child_data.count() > 0:
                    print(instance.pk)
                    for data in child_data:
                        if instance.response_set.filter(milestone__second_code=data.data_key, response='done').count() < 1:
                            response = Response.objects.create(instance=instance,
                                                               milestone=Milestone.objects.get(second_code=data.data_key),
                                                               response='done',
                                                               created_at=data.timestamp)
                            print(instance.pk, response.milestone, response.response)
                            count = count + 1

    print(count)
