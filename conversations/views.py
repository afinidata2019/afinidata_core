from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from messenger_users.models import User, UserData, UserChannel
from attributes.models import Attribute
from entities.models import Entity
from django.http import JsonResponse, Http404
from conversations import forms
from bots.models import Interaction, UserInteraction
from django.utils import timezone
from user_sessions.models import BotSessions
from datetime import datetime
import requests
import os


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

        user_channel = UserChannel.objects.filter(user_channel_id=user_channel_id,
                                                  bot_id=bot_id,
                                                  channel_id=channel_id,
                                                  bot_channel_id=bot_channel_id)
        endpoints = dict(get_field=os.getenv("CONTENT_MANAGER_URL")+'/chatfuel/get_session_field/',
                         get_session=os.getenv("CONTENT_MANAGER_URL")+'/chatfuel/get_session/',
                         save_reply=os.getenv("CONTENT_MANAGER_URL")+'/chatfuel/save_last_reply/',
                         create_user=os.getenv("CONTENT_MANAGER_URL")+'/chatfuel/create_messenger_user/',
                         get_info=os.getenv("WEBHOOK_DOMAIN_URL")+'/bots/'+str(bot_id)+'/channel/'+str(bot_channel_id)+'/get_user_info/',
                         get_data=os.getenv("WEBHOOK_DOMAIN_URL")+'/bots/'+str(bot_id)+'/channel/'+str(bot_channel_id)+'/get_user_data/')
        response = []
        if not user_channel.exists():
            service_response = requests.post(endpoints['create_user'],
                                             data=dict(channel_id=user_channel_id,
                                                       bot_id=bot_id,
                                                       first_name=user_channel_id,
                                                       last_name='None')).json()
            user = User.objects.get(id=service_response['set_attributes']['user_id'])
            user_channel = UserChannel.objects.create(bot_id=bot_id,
                                                      channel_id=channel_id,
                                                      bot_channel_id=bot_channel_id,
                                                      user_channel_id=user_channel_id,
                                                      user=user)
            # Get user data from channel
            try:
                service_params = dict(user_channel_id=user_channel_id)
                service_response = requests.post(endpoints['get_info'], data=service_params).json()
                if 'request_status' in service_response and service_response['request_status'] == 'done':
                    for data_key in service_response['data']:
                        if data_key == 'first_name':
                            user.first_name = service_response['data'][data_key]
                            user.save()
                        elif data_key == 'last_name':
                            user.last_name = service_response['data'][data_key]
                            user.save()
                        elif data_key != 'id':
                            # Crear el atributo si no existe
                            attribute, created = Attribute.objects.get_or_create(name=data_key)
                            # Asocial el atributo al usuario Encargado/Pregnant
                            Entity.objects.get(id=4).attributes.add(attribute)
                            Entity.objects.get(id=5).attributes.add(attribute)
                            # Agregar el atributo al usuario
                            UserData.objects.create(data_key=data_key,
                                                    user_id=user.id,
                                                    data_value=service_response['data'][data_key],
                                                    attribute_id=attribute.id)
            except:
                pass
            # Get bot Welcome register session:
            session = BotSessions.objects.filter(bot_id=bot_id, session_type='welcome')
            if session.exists():
                session = session.last().session_id
            else:
                session = 0
            service_params = dict(user_id=user.id,
                                  session=session)
            service_response = requests.post(endpoints['get_session'], data=service_params).json()
            session_finish = service_response['set_attributes']['session_finish']

            # Crear interaccion de inicio de registro
            bot_interaction = Interaction.objects.get(name='start_registration')
            UserInteraction.objects.create(bot_id=bot_id, user_id=user.id,
                                           interaction=bot_interaction, value=0,
                                           created_at=timezone.now(), updated_at=timezone.now())
        else:
            user_channel = user_channel.last()
            user = user_channel.user

        # Save last seen datetime
        user_channel.last_seen = datetime.now()
        user_channel.save()
        user.last_seen = datetime.now()
        user.save()

        # If user is in live-chat, don't process message in bot
        if user_channel.live_chat:
            return JsonResponse(dict(response=[]))
        try:
            # Get ref
            for data_key in ['ref']:
                service_params = dict(user_channel_id=user_channel_id,
                                      attribute_key=data_key)
                service_response = requests.post(endpoints['get_data'], data=service_params).json()
                if 'request_status' in service_response and service_response['request_status'] == 'done':
                    # Crear el atributo si no existe
                    attribute, created = Attribute.objects.get_or_create(name=data_key)
                    # Asocial el atributo al usuario Encargado/Pregnant
                    Entity.objects.get(id=4).attributes.add(attribute)
                    Entity.objects.get(id=5).attributes.add(attribute)
                    # Agregar el atributo al usuario
                    UserData.objects.create(data_key=data_key,
                                            user_id=user.id,
                                            data_value=service_response['data']['attribute_value'],
                                            attribute_id=attribute.id)
                    # Llamar al servicio de creación de usuario nuevamente para que
                    #  asigne al usuario al grupo y canjee el código
                    requests.post(endpoints['create_user'],
                                  data=dict(channel_id=user_channel_id,
                                            bot_id=bot_id,
                                            first_name=user.first_name,
                                            last_name=user.last_name,
                                            ref=service_response['data']['attribute_value']))
        except:
            pass
        if user_message.lower() != 'dont_save':
            try:
                # Save user message
                service_params = dict(user_id=user.id,
                                    last_reply=user_message,
                                    bot_id=bot_id)
                requests.post(endpoints['save_reply'], data=service_params)
            except:
                pass
        try:
            first_message = True
            # Is session finished
            session_finish = user.userdata_set.filter(attribute__name='session_finish')
            if session_finish.exists():
                session_finish = session_finish.last().data_value
            else:
                session_finish = 'true'
            # Get the first message
            service_params = dict(user_id=user.id)
            service_response = requests.post(endpoints['get_field'], data=service_params).json()

            # If the session is already finished
            if session_finish.lower() == 'true':
                # Get bot default session:
                session = BotSessions.objects.filter(bot_id=bot_id, session_type='default')
                if session.exists():
                    session = session.last().session_id
                else:
                    session = 0
                service_params = dict(user_id=user.id,
                                      session=session)
                service_response = requests.post(endpoints['get_session'], data=service_params).json()
                session_finish = service_response['set_attributes']['session_finish']
                first_message = False

                # Crear interaccion de inicio de default
                bot_interaction = Interaction.objects.get(name='default')
                UserInteraction.objects.create(bot_id=bot_id, user_id=user.id,
                                               interaction=bot_interaction, value=0,
                                               created_at=timezone.now(), updated_at=timezone.now())

            while session_finish.lower() == 'false' and not user_channel.live_chat:
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
                                                 quick_replies=[qr['title'] for qr in message['quick_replies']]))
                        elif 'text' in message:
                            response.append(dict(bot_id=bot_id,
                                                 channel_id=channel_id,
                                                 user_channel_id=user_channel_id,
                                                 bot_channel_id=bot_channel_id,
                                                 type='text' if 'OTN' not in message else 'one_time_notification',
                                                 content=message['text']))
                            if 'OTN' in message:
                                session_finish = 'true'
                        elif 'attachment' in message:
                            if 'type' in message['attachment']:
                                if message['attachment']['type'] == 'image':
                                    response.append(dict(bot_id=bot_id,
                                                         channel_id=channel_id,
                                                         user_channel_id=user_channel_id,
                                                         bot_channel_id=bot_channel_id,
                                                         type='image',
                                                         content=message['attachment']['payload']['url']))
                                elif message['attachment']['type'] == 'template':
                                    if message['attachment']['payload']['template_type'] == 'button':
                                        buttons = message['attachment']['payload']['buttons']
                                        response.append(dict(bot_id=bot_id,
                                                             channel_id=channel_id,
                                                             user_channel_id=user_channel_id,
                                                             bot_channel_id=bot_channel_id,
                                                             type='text',
                                                             content=message['attachment']['payload']['text']))

                                    elif message['attachment']['payload']['template_type'] == 'media':
                                        buttons = message['attachment']['payload']['elements'][0]['buttons']
                                        response.append(dict(bot_id=bot_id,
                                                             channel_id=channel_id,
                                                             user_channel_id=user_channel_id,
                                                             bot_channel_id=bot_channel_id,
                                                             type='image',
                                                             content=message['attachment']['payload']['elements'][0]['url']))
                                    for button in buttons:
                                        response.append(dict(bot_id=bot_id,
                                                             channel_id=channel_id,
                                                             user_channel_id=user_channel_id,
                                                             bot_channel_id=bot_channel_id,
                                                             type='button',
                                                             content=button['title'],
                                                             url=button['url']))

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
            if len(response) == 0:
                # Get bot default session:
                session = BotSessions.objects.filter(bot_id=bot_id, session_type='default')
                if session.exists():
                    session = session.last().session_id
                else:
                    session = 0
                service_params = dict(user_id=user.id,
                                      session=session)
                service_response = requests.post(endpoints['get_session'], data=service_params).json()
                return JsonResponse(dict(response=[]))
        except:
            # Get bot default session:
            session = BotSessions.objects.filter(bot_id=bot_id, session_type='default')
            if session.exists():
                session = session.last().session_id
            else:
                session = 0
            service_params = dict(user_id=user.id,
                                  session=session)
            service_response = requests.post(endpoints['get_session'], data=service_params).json()
            return JsonResponse(dict(response=[]))
        return JsonResponse(dict(response=response))
