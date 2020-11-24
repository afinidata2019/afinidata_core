from rest_framework import serializers
from .models import Field, Service, ServiceParam

class ServiceParamSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceParam
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):

    serviceparam_set = ServiceParamSerializer(many=True)

    class Meta:
        model = Service
        fields = ['id','url','field','serviceparam_set']

class FieldSerializer(serializers.ModelSerializer):
    service = ServiceSerializer()

    class Meta:
        model = Field
        fields = ('id','position','field_type','field_type_display','message_set','button_set','setattribute_set','userinput_set','reply_set','condition_set','redirectblock','redirectsession','service')
        depth = 2
