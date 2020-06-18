from posts.models import Post, Feedback, Question
from core.settings import BASE_DIR
from dateutil.parser import parse
import csv
import sys
import os


def run():

    if len(sys.argv) < 4 or len(sys.argv) > 4:
        return None

    date_text = sys.argv[3]
    date = parse(date_text)

    posts = Post.objects.filter(status='published').only('id', 'name')
    with open(os.path.join(BASE_DIR, 'posts-info-%s.csv' % date_text), 'w', newline='') as csvfile:

        fieldnames = ['ID', 'Name', 'Feedback', 'Comentarios']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for post in posts:
            print(post)
            f_counter = 0
            f_total = 0
            f_data = 0
            comments = ''
            for f in post.feedback_set.filter(created_at__gte=date):
                print(f.created_at)
                f_total = f_total + f.value
                f_counter = f_counter + 1
            if f_counter > 0:
                f_data = "{:.2f}".format(f_total / f_counter)
            for c in post.messengerusercommentpost_set.filter(created_at__gte=date):
                comments = comments + "%s |  \n" % c.comment
            print(f_data)
            data = dict(ID=post.pk, Name=post.name, Feedback=f_data, Comentarios=comments)
            writer.writerow(data)
