from posts.models import Response, QuestionResponse, Post
from instances.models import InstanceFeedback
from messenger_users.models import User


def run():

    limit = InstanceFeedback.objects.filter(register_type=0)
    if limit.count() > 0:
        print("limit: ", limit.last().register_id)
        qs = Response.objects.filter(id__gt=limit.last().register_id)
    else:
        qs = Response.objects.all()

    for r in qs:
        post_id = r.question.post_id
        value = None
        try:
            value = int(r.response)
        except Exception as e:
            pass

        if value:
            posts = Post.objects.filter(id=post_id).only('id', 'area_id', 'name')
            if posts.count() > 0:
                post = posts.last()
                users = User.objects.filter(id=r.user_id)
                if users.count() > 0:
                    user = users.last()
                    children = user.get_instances().filter(entity_id=1)
                    if children.count() > 0:
                        child = children.last()
                        responses = QuestionResponse.objects.filter(question=r.question, value=value)
                        if responses.count() > 0:
                            response = responses.last()
                            print(response.pk, response.response)
                            new_feed = InstanceFeedback.objects\
                                .create(instance=child, post_id=post.pk, area_id=post.area_id, value=value,
                                        reference_text=response.response, register_id=r.pk, register_type=0,
                                        migration_field_id=response.pk, created_at=r.created_at)
                            print(new_feed)
