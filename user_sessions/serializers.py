from rest_framework import serializers
from .models import Field

class FieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = Field
        fields = ('id','position','field_type','field_type_display','message_set','button_set','setattribute_set','userinput_set','reply_set','condition_set','redirectblock','redirectsession')
        depth = 2
