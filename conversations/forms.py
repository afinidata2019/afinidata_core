from django import forms


class ConversationWorkflowForm(forms.Form):
    bot_id = forms.IntegerField()
    bot_channel_id = forms.IntegerField()
    channel_id = forms.IntegerField()
    user_channel_id = forms.IntegerField()
    message = forms.CharField(required=False)
