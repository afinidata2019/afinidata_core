from django.db import models
from entities.models import Entity
from bots import models as bot_models
from areas.models import Area, Section
from milestones.models import Milestone
from attributes.models import Attribute
from messenger_users import models as user_models
from posts.models import Post


class Instance(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    attributes = models.ManyToManyField(Attribute, through='AttributeValue')
    milestones = models.ManyToManyField(Milestone, through='Response')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (
            ('view_all_instances', 'User can view all instances'),
        )

    def __str__(self):
        return self.name

    def get_time_interactions(self, first_limit, last_limit):
        interactions = self.postinteraction_set.filter(created_at__gte=first_limit, created_at__lte=last_limit)
        return interactions

    def get_users(self):
        return user_models.User.objects\
            .filter(id__in=set(assoc.user_id for assoc in self.instanceassociationuser_set.all()))

    def get_assigned_milestones(self):
        milestones = self.get_completed_milestones().union(self.get_failed_milestones()).order_by('-code')
        for milestone in milestones:
            milestone.assign = self.response_set.filter(milestone=milestone).order_by('-created_at').first()
        return milestones

    def get_completed_milestones(self):
        milestones = Milestone.objects.filter(
            id__in=[m.milestone.pk for m in self.response_set.filter(response='done')])
        for milestone in milestones:
            milestone.assign = self.response_set.filter(milestone=milestone).filter(response='done') \
                .order_by('-created_at').first()
        return milestones

    def get_failed_milestones(self):
        milestones = Milestone.objects.filter(id__in=[m.milestone.pk for m in self.response_set.exclude(response='done')])
        for milestone in milestones:
            milestone.assign = self.response_set.filter(milestone=milestone).exclude(response='done')\
                .order_by('-created_at').first()
        return milestones

    def get_activities(self):
        posts = Post.objects.filter(id__in=set([x.post_id for x in self.postinteraction_set.all()])).only('id', 'name')
        for post in posts:
            post.assign = self.postinteraction_set.filter(post_id=post.id, type='dispatched').last()
            sessions = self.postinteraction_set.filter(post_id=post.id, type='session')
            if sessions.count() > 0:
                post.completed = sessions.last()
            else:
                post.completed = None
        return posts

    def get_completed_activities(self):
        posts = Post.objects\
            .filter(id__in=set([x.post_id for x in self.postinteraction_set.filter(type='session')])).only('id')
        return posts

    def get_attributes(self):
        attributes_ids = set(item.pk for item in self.attributes.all())
        attributes = Attribute.objects.filter(id__in=attributes_ids)
        for attribute in attributes:
            attribute.assign = self.attributevalue_set.filter(attribute=attribute).last()
        return attributes


class InstanceAssociationUser(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Score(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    value = models.FloatField(default=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.instance.name + '__' + self.area.name + '__' + str(round(self.value, 2))


class ScoreTracking(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    value = models.FloatField(default=0, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.instance.name + '__' + self.area.name + '__' + str(round(self.value, 2))


class Response(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    response = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s__%s__%s%s__%s" % (self.pk, self.instance.name, self.milestone.pk, self.milestone.name, self.response)


class AttributeValue(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s__%s__%s__%s" % (self.pk, self.instance.name, self.attribute.name, self.value)


class PostInteraction(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    post_id = models.IntegerField()
    type = models.CharField(max_length=255, default='open')
    value = models.IntegerField(default=0)
    created_at = models.DateTimeField()

    def __str__(self):
        return "%s %s %s %s" % (self.pk, self.instance, self.post_id, self.type)
