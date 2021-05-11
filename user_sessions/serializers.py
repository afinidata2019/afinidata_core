from rest_framework import serializers
from .models import Field, Service, ServiceParam, AvailableService, AssignSequence, UnsubscribeSequence
import requests
import os


class ServiceParamSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceParam
        fields = '__all__'


class AvailableServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = AvailableService
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):

    serviceparam_set = ServiceParamSerializer(many=True)
    available_service = AvailableServiceSerializer(many=False)

    class Meta:
        model = Service
        fields = ['id', 'field', 'available_service', 'serviceparam_set']


class SubscribeSequenceSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')

    def get_name(self, obj):
        response = requests.get(os.getenv("HOTTRIGGERS_API") + '/sequences/?id=' + str(obj.sequence_id))
        name = obj.sequence_id
        if response.status_code == 200:
            if len(response.json()['results']) > 0:
                name = "%s (%s)" % (response.json()['results'][0]['name'], response.json()['results'][0]['description'])
        return name

    class Meta:
        model = AssignSequence
        fields = ('id', 'field', 'sequence_id', 'name', 'start_position', 'created_at', 'updated_at')


class UnsubscribeSequenceServiceSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')

    def get_name(self, obj):
        response = requests.get(os.getenv("HOTTRIGGERS_API") + '/sequences/?id=' + str(obj.sequence_id))
        name = obj.sequence_id
        if response.status_code == 200:
            if len(response.json()['results']) > 0:
                name = "%s (%s)" % (response.json()['results'][0]['name'], response.json()['results'][0]['description'])
        return name

    class Meta:
        model = UnsubscribeSequence
        fields = ('id', 'field', 'sequence_id', 'name', 'created_at', 'updated_at')


class FieldSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()
    assignsequence = SubscribeSequenceSerializer()
    unsubscribesequence = UnsubscribeSequenceServiceSerializer()

    class Meta:
        model = Field
        fields = ('id', 'position', 'field_type', 'field_type_display', 'message_set', 'button_set', 'setattribute_set',
                  'userinput_set', 'reply_set', 'condition_set', 'redirectblock', 'redirectsession', 'assignsequence',
                  'unsubscribesequence', 'service')
        depth = 2
