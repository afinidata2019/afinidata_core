from milestones.models import Milestone
from languages.models import Language
from areas.models import Area
from django.db import models


class Program(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(null=True, blank=True)
    languages = models.ManyToManyField(Language)
    levels = models.ManyToManyField('Level')
    areas = models.ManyToManyField(Area)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ('view_all_programs', 'User can view all programs'),
            ('view_user_programs', 'User can view programs in your groups')
        )


class Level(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    assign_min = models.IntegerField(null=True, blank=True, default=0)
    assign_max = models.IntegerField(null=True, blank=True, default=1)
    milestones = models.ManyToManyField(Milestone, through='LevelMilestoneAssociation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%s - %s  Months)" % (self.name, self.assign_min, self.assign_max)


class LevelMilestoneAssociation(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

