from posts.models import Post, Feedback, Question
from core.settings import BASE_DIR
import csv
import os


def run():
    posts = Post.objects.all().only('id', 'name')
    with open(os.path.join(BASE_DIR, 'posts_info.csv'), 'w', newline='') as csvfile:

        fieldnames = ['ID', 'Name', 'Feedback', 'Comentarios']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for post in posts:
            print(post)
            f_counter = 0
            f_total = 0
            f_data = 0
            comments = ''
            for f in post.feedback_set.all():
                f_total = f_total + f.value
                f_counter = f_counter + 1
            if f_counter > 0:
                f_data = "{:.2f}".format(f_total / f_counter)
            for c in post.messengerusercommentpost_set.all():
                comments = comments + "%s |  \n" % c.comment
            print(f_data)
            data = dict(ID=post.pk, Name=post.name, Feedback=f_data, Comentarios=comments)
            writer.writerow(data)

