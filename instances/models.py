from django.db import models
from entities.models import Entity
from bots.models import Bot
from areas.models import Area, Section
from milestones.models import Milestone
from attributes.models import Attribute
from messenger_users.models import User


class Instance(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    attributes = models.ManyToManyField(Attribute, through='AttributeValue')
    sections = models.ManyToManyField(Section, through='InstanceSection')
    areas = models.ManyToManyField(Area, through='InstanceSection')
    milestones = models.ManyToManyField(Milestone, through='Response')
    user_id = models.IntegerField(default=1, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_messenger_user(self):
        return User.objects.get(id=self.user_id)


class InstanceSection(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    value_to_init = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s__%s__%s" % (self.pk, self.instance.pk, self.section.pk)


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
