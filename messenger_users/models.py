from instances import models as InstanceModels
from bots.models import Bot
from django.db import models
import uuid

PRE_REGISTER = 'pre_register'
IN_REGISTRATION = 'in_registration'
USER_DEAD = 'user_dead'
WAIT = 'wait'
USER_QUERY = 'user_query'
BROADCAST_START = 'broadcast_start'
TIMED_START = 'timed_start'
ACTIVE_SESSION = 'active_session'
PRE_CHURN = 'pre_churn'
DISPATCHED = 'dispatched'
OPENED = 'opened'
FOLLOW_UP = 'follow_up'

# Transition consts

START_REGISTER = 'start_register'
FINISH_REGISTER = 'finish_register'
USER_DIE = 'decay'
RECEIVE_USER_MESSAGE = 'receive_user_message'
SEND_BROADCAST = 'send_broadcast'
AWAITED_ENOUGH = 'awaited_enough'
WANT_ACTIVITY = 'want_activity'
GET_POST = 'get_post'
SET_PRE_CHURN = 'set_pre_churn'
OPEN_POST = 'open_post'
NO_OPEN = 'no_open'
GIVE_FEEDBACK = 'give_feedback'
END_FEEDBACK = 'end_feedback'
NO_FEEDBACK = 'no_feedback'

STATE_TYPES = [
    (PRE_REGISTER, PRE_REGISTER),
    (IN_REGISTRATION, IN_REGISTRATION),
    (USER_DEAD, USER_DEAD),
    (WAIT, WAIT),
    (USER_QUERY, USER_QUERY),
    (BROADCAST_START, BROADCAST_START),
    (TIMED_START, TIMED_START),
    (ACTIVE_SESSION, ACTIVE_SESSION),
    (PRE_CHURN, PRE_CHURN),
    (DISPATCHED, DISPATCHED),
    (OPENED, OPENED),
    (FOLLOW_UP, FOLLOW_UP),
]


class User(models.Model):
    last_channel_id = models.CharField(max_length=50, unique=True)
    channel_id = models.CharField(max_length=50, unique=True)
    backup_key = models.CharField(max_length=50, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    bot_id = models.IntegerField(default=1)
    username = models.CharField(max_length=100, null=True, unique=True)

    def __str__(self):
        return self.username

    def get_first_name(self):
        names = self.userdata_set.filter(data_key='channel_first_name')
        if names.count() > 0:
            return names.last().data_value
        else:
            return None

    def get_last_name(self):
        names = self.userdata_set.filter(data_key='channel_last_name')
        if names.count() > 0:
            return names.last().data_value
        else:
            return None

    def get_instances(self):
        return InstanceModels.Instance.objects.filter(instanceassociationuser__user_id=self.pk)

    def get_bot(self):
        return Bot.objects.get(id=self.bot_id)

    def get_email(self):
        keys = self.userdata_set.filter(data_key='email')
        print(keys)
        if keys.count() > 0:
            return keys.last().data_value
        else:
            return None

    def get_country(self):
        keys = self.userdata_set.filter(data_key='Pais')
        print(keys)
        if keys.count() > 0:
            return keys.last().data_value
        else:
            return None

    def get_property(self, data_key):
        keys = self.userdata_set.filter(data_key=data_key)
        print(keys)
        if keys.count() > 0:
            return keys.last().data_value
        else:
            return None


class UserData(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    data_key = models.CharField(max_length=30)
    data_value = models.TextField()
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.data_value


class Child(models.Model):
    parent_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=50)
    dob = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now=True)


class ChildData(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    data_key = models.CharField(max_length=50)
    data_value = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.pk


class Referral(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_shared = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='shared_ref')
    user_opened = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='opened_ref', null=True)
    ref_type = models.CharField(choices=[("link", "link"), ("ref","ref")], default="link", max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "User '{}' referred '{}'".format(self.user_shared, self.user_opened)


class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    initial_state = models.CharField(max_length=25)
    final_state = models.CharField(max_length=25)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)


class UserActivity(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    last_change = models.DateTimeField(auto_now=True)
    state = models.CharField(
        "state",
        max_length=100,
        choices=STATE_TYPES,
        default=WAIT,
        help_text='stado',
    )

