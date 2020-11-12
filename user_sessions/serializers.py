from rest_framework import serializers
from .models import Field, Service

class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ('__all__, serviceparam_set')

class FieldSerializer(serializers.ModelSerializer):

    service = ServiceSerializer(many=True)

    class Meta:
        model = Field
        fields = ('id','position','field_type','field_type_display','message_set','button_set','setattribute_set','userinput_set','reply_set','condition_set','redirectblock','redirectsession','service')
        depth = 2
