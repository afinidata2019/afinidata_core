from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from messenger_users.models import User, UserData, UserChannel
from django.http import JsonResponse, Http404
from chatfuel import forms
import requests


@method_decorator(csrf_exempt, name='dispatch')
class ConversationWorkflow(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request, *args, **kwargs):
        form = forms.ConversationWorkflowForm(request.POST)
        bot_id = form.data['bot_id']
        bot_channel_id = form.data['bot_channel_id']
        channel_id = form.data['channel_id']
        user_channel_id = form.data['user_channel_id']
        user_message = form.data['message']
        user_channel = UserChannel.objects.filter(user_channel_id=user_channel_id)
        endpoints = dict(get_field='https://contentmanager.afinidata.com/chatfuel/get_session_field/',
                         get_session='https://contentmanager.afinidata.com/chatfuel/get_session/',
                         save_reply='https://contentmanager.afinidata.com/chatfuel/save_last_reply/',
                         create_user='https://contentmanager.afinidata.com/chatfuel/create_messenger_user/')
        response = []
        if not user_channel.exists():
            service_response = requests.post(endpoints['create_user'],
                                             data=dict(channel_id=user_channel_id,
                                                       bot_id=bot_id,
                                                       first_name='Estuardo',
                                                       last_name='Díaz')).json()
            user = User.objects.get(id=service_response['set_attributes']['user_id'])
            UserChannel.objects.create(bot_id=bot_id,
                                       channel_id=channel_id,
                                       bot_channel_id=bot_channel_id,
                                       user_channel_id=user_channel_id,
                                       user=user)
        else:
            user = user_channel.last().user

        try:
            # Save user message
            service_params = dict(user_id=user.id,
                                  last_reply=user_message,
                                  bot_id=bot_id)
            requests.post(endpoints['save_reply'], data=service_params)
        except:
            pass

        first_message = True
        # Get the first message
        service_params = dict(user_id=user.id)
        service_response = requests.post(endpoints['get_field'], data=service_params).json()
        session_finish = service_response['set_attributes']['session_finish']

        # If the session is already finished
        if session_finish == 'true':
            # Get bot default session:
            session = 603
            service_params = dict(user_id=user.id,
                                  session=session)
            service_response = requests.post(endpoints['get_session'], data=service_params).json()
            session_finish = service_response['set_attributes']['session_finish']
            first_message = False

        while session_finish == 'false':
            if not first_message:
                # Get the next message
                service_params = dict(user_id=user.id)
                service_response = requests.post(endpoints['get_field'], data=service_params).json()
                session_finish = service_response['set_attributes']['session_finish']

            first_message = False
            save_user_input = False
            if 'save_user_input' in service_response['set_attributes']:
                save_user_input = service_response['set_attributes']['save_user_input']
            save_text_reply = False
            if 'save_text_reply' in service_response['set_attributes']:
                save_text_reply = service_response['set_attributes']['save_text_reply']
            if 'messages' in service_response:
                for message in service_response['messages']:
                    if 'quick_replies' in message:
                        response.append(dict(bot_id=bot_id,
                                             channel_id=channel_id,
                                             user_channel_id=user_channel_id,
                                             bot_channel_id=bot_channel_id,
                                             type='quick_replies',
                                             content=message['text'],
                                             quick_replies=[qr['title'] for qr in message['quick_replies']]
                                             ))
                    else:
                        if 'text' in message:
                            response.append(dict(bot_id=bot_id,
                                                 channel_id=channel_id,
                                                 user_channel_id=user_channel_id,
                                                 bot_channel_id=bot_channel_id,
                                                 type='text',
                                                 content=message['text']))
            if 'set_attributes' in service_response:
                if 'user_input_text' in service_response['set_attributes']:
                    response.append(dict(bot_id=bot_id,
                                         channel_id=channel_id,
                                         user_channel_id=user_channel_id,
                                         bot_channel_id=bot_channel_id,
                                         type='text',
                                         content=service_response['set_attributes']['user_input_text']))
            if save_user_input or save_text_reply:
                session_finish = 'true'
        return JsonResponse(dict(response=response))
