from messenger_users.models import User
from core.settings import BASE_DIR
from groups.models import Group
from posts.models import Post
import sys
import csv
import os


def run():
    if len(sys.argv) < 4 or len(sys.argv) > 4:
        return None

    group_name = sys.argv[3]
    try:
        group = Group.objects.get(name=group_name)
        user_set = set(assign.messenger_user_id for assign in group.assignationmessengeruser_set.all())
        users = User.objects.filter(id__in=user_set)
        posts_id = set()
        for user in users:
            for i in user.get_instances():
                for inter in i.postinteraction_set.all():
                    posts_id.add(inter.post_id)
        posts = Post.objects.filter(id__in=posts_id).only('id', 'name')
        print(posts_id)

        with open(os.path.join(BASE_DIR, '%s-posts-core.csv' % (group_name + '__activities')), 'w', newline='') as csvfile:
            fieldnames = ['post_id', 'name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for post in posts:
                writer.writerow(dict(post_id=post.pk, name=post.name))

    except Exception as e:
        print(e)
        print('not possible get data.')
