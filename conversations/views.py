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

        endpoints = dict(
            # NLU
            nlu_reply=os.getenv('NLU_DOMAIN') + '/get_intended_reply/',
            nlu_interpret=os.getenv('NLU_DOMAIN') + '/get_intent/',
            # CM API
            user=os.getenv("CONTENT_MANAGER_API") + '/messenger_users/',
            user_channel=os.getenv("CONTENT_MANAGER_API") + '/messenger_users_channels/',
            # CM
            create_user_channel=os.getenv("CONTENT_MANAGER_DOMAIN") + '/chatfuel/create_messenger_user_channel/',
            get_previous_field=os.getenv("CONTENT_MANAGER_DOMAIN") + '/chatfuel/get_user_previous_field/',
            get_field=os.getenv("CONTENT_MANAGER_DOMAIN") + '/chatfuel/get_session_field/',
            get_session=os.getenv("CONTENT_MANAGER_DOMAIN") + '/chatfuel/get_session/',
            save_reply=os.getenv("CONTENT_MANAGER_DOMAIN") + '/chatfuel/save_last_reply/',
            create_user=os.getenv("CONTENT_MANAGER_DOMAIN") + '/chatfuel/create_messenger_user/',
            # Webhook
            get_info=os.getenv("WEBHOOK_DOMAIN") + '/bots/' + str(bot_id) + '/channel/' + str(
                bot_channel_id) + '/get_user_info/',
            get_data=os.getenv("WEBHOOK_DOMAIN") + '/bots/' + str(bot_id) + '/channel/' + str(
                bot_channel_id) + '/get_user_data/'
        )
        response = []
        # check if the user channel already exists
        user_channel = self.get_user_channel(
            dict(user_channel_id=user_channel_id, bot_id=bot_id, channel_id=channel_id, bot_channel_id=bot_channel_id))

        if user_channel:
            user_id = user_channel['user']['id']
        else:
            service_response = requests.post(endpoints['create_user'], data=dict(bot_id=bot_id,
                                                                                 channel_id=user_channel_id,
                                                                                 first_name=user_channel_id,
                                                                                 last_name='None')).json()
            user_id = service_response['set_attributes']['user_id']

            # create userchannel
            user_channel = requests.post(endpoints['user_channel'], dict(bot_id=bot_id,
                                                                         channel_id=channel_id,
                                                                         bot_channel_id=bot_channel_id,
                                                                         user_channel_id=user_channel_id,
                                                                         user=user_id)).json()
            user_channel = user_channel['data']

            # Get user data from channel
            try:
                service_params = dict(user_channel_id=user_channel_id)
                service_response = requests.post(endpoints['get_info'], data=service_params).json()

                if 'request_status' in service_response and service_response['request_status'] == 'done':
                    for data_key in service_response['data']:
                        if data_key == 'first_name':
                            requests.patch(endpoints['user'],
                                           dict(id=user_id, first_name=service_response['data'][data_key]))

                        elif data_key == 'last_name':
                            requests.patch(endpoints['user'],
                                           dict(id=user_id, last_name=service_response['data'][data_key]))

                        elif data_key == 'ref':
                            if service_response['data'][data_key] != '' and service_response['data'][
                                data_key] is not None:
                                # Agregar el ref al usuario solo si no viene vacío
                                self.create_associate_user_attribute(user_id, data_key,
                                                                     data_value=service_response['data'][data_key])
                        elif data_key != 'id':
                            # Crear el atributo si no existe, Asocial el atributo al usuario Encargado/Profesional
                            # y Agregar el atributo al usuario
                            self.create_associate_user_attribute(user_id, data_key,
                                                                 data_value=service_response['data'][data_key])
            except Exception as e:
                pass

            # Get bot Welcome register session and returns if it's finished:
            service_response = self.get_bot_session(user_id, bot_id, session_type='welcome')
            session_finish = service_response['set_attributes']['session_finish']

            # Crear interaccion de inicio de registro
            self.create_interaction(bot_id, user_id, name='start_registration')

        # Save last seen datetime
        requests.patch(endpoints['user'] + str(user_id) + '/', dict(last_seen=datetime.now()))
        requests.patch(endpoints['user_channel'] + str(user_channel['id']) + '/', dict(last_seen=datetime.now()))

        # If user is in live-chat, don't process message in bot
        if user_channel['live_chat']:
            return JsonResponse(dict(response=[]))
        try:
            # Get ref
            for data_key in ['ref']:
                service_params = dict(user_channel_id=user_channel_id, attribute_key=data_key)
                service_response = requests.post(endpoints['get_data'], data=service_params).json()
                if 'request_status' in service_response and service_response['request_status'] == 'done':
                    if service_response['data']['attribute_value'] != '' and service_response['data'][
                        'attribute_value'] is not None:
                        # Crear el atributo si no existe, Asocial el atributo al usuario Encargado/Profesional
                        # y Agregar el atributo al usuario
                        self.create_associate_user_attribute(user_id, data_key,
                                                             data_value=service_response['data']['attribute_value'])

                        # Llamar al servicio de creación de usuario nuevamente para que
                        #  asigne al usuario al grupo y canjee el código
                        service_response = requests.post(endpoints['create_user'],
                                                         data=dict(channel_id=user_channel_id,
                                                                   bot_id=bot_id,
                                                                   ref=service_response['data'][
                                                                       'attribute_value'])).json()
                        user_id = service_response['set_attributes']['user_id']
        except Exception as e:
            pass

        # parameters needed by the webhook to send the bot's reply
        reply_params = dict(bot_id=bot_id,
                            channel_id=channel_id,
                            user_channel_id=user_channel_id,
                            bot_channel_id=bot_channel_id)

        # Save user message
        if user_message.lower().strip() != 'dont_save':
            try:
                service_params = dict(user_id=user_id,
                                      last_reply=user_message,
                                      bot_id=bot_id)

                AI_active = self.get_user_data_attribute(user_id, 'AI_active')

                is_quick_reply = False
                previous_field = requests.post(endpoints['get_previous_field'], data=dict(user_id=user_id)).json()
                if ('request_status' in previous_field and previous_field['request_status'] == 200 and previous_field[
                    'field']
                        and previous_field['field']['field_type'] == 'quick_replies'):
                    is_quick_reply = True

                # check if message should be interpreted
                if AI_active or is_quick_reply:

                    if is_quick_reply and user_message not in previous_field['replies']:
                        # fetch intended response from NLU service if response is not recognized
                        nlu_response = requests.post(endpoints['nlu_reply'], json=dict(sender=user_channel_id,
                                                                                       message=user_message,
                                                                                       options=previous_field[
                                                                                           'replies'])).json()

                        if nlu_response['request_status'] == 200:
                            service_params['last_reply'] = nlu_response['text']

                    if AI_active and (
                            not is_quick_reply or service_params['last_reply'] not in previous_field['replies']):
                        # get user intent
                        nlu_response = requests.post(endpoints['nlu_interpret'], data=dict(sender=user_channel_id,
                                                                                           message=service_params[
                                                                                               'last_reply'])).json()

                        if nlu_response['request_status'] == 200:
                            if 'text' in nlu_response['data']:
                                response.append(dict(**reply_params,
                                                     type='text',
                                                     content=nlu_response['data']['text']))
                            elif 'session' in nlu_response['data']:
                                # Redirect to the new session
                                redirect_params = dict(user_id=user_id,
                                                       session=nlu_response['data']['session'])
                                requests.post(endpoints['get_session'], data=redirect_params).json()
                # save reply
                requests.post(endpoints['save_reply'], data=service_params)

            except Exception as e:
                pass

        try:
            first_message = True
            session_finish = self.get_user_data_attribute(user_id, 'session_finish', default='true')

            # Get the first message
            service_params = dict(user_id=user_id)
            service_response = requests.post(endpoints['get_field'], data=service_params).json()
            if 'user_id' in service_response['set_attributes']:
                user_id = service_response['set_attributes']['user_id']

            # If the session is already finished
            if session_finish.lower() == 'true':
                # Get bot default session:
                service_response = self.get_bot_session(user_id, bot_id, session_type='default')
                session_finish = service_response['set_attributes']['session_finish']
                first_message = False

                # Crear interaccion de inicio de default
                self.create_interaction(bot_id, user_id, name='default')

            # refresh userchannel
            user_channel = self.get_user_channel(dict(id=user_channel['id']))

            while session_finish.lower() == 'false' and not user_channel['live_chat']:
                if not first_message:
                    # Get the next message
                    service_params = dict(user_id=user_id)
                    service_response = requests.post(endpoints['get_field'], data=service_params).json()
                    session_finish = service_response['set_attributes']['session_finish']
                    if 'user_id' in service_response['set_attributes']:
                        user_id = service_response['set_attributes']['user_id']

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
                            response.append(dict(**reply_params,
                                                 type='quick_replies',
                                                 content=message['text'],
                                                 quick_replies=[qr['title'] for qr in message['quick_replies']]))
                        # OTN also contains the key 'text', hence it must be tested before simple text or add a condition to text
                        elif 'OTN' in message:
                            session_finish = 'true'
                            response.append(dict(**reply_params,
                                                 type='one_time_notification',
                                                 content=message['text']))
                        elif 'text' in message:
                            response.append(dict(**reply_params,
                                                 type='text',
                                                 content=message['text']))
                        elif 'attachment' in message:
                            if 'type' in message['attachment']:
                                if message['attachment']['type'] == 'image':
                                    response.append(dict(**reply_params,
                                                         type='image',
                                                         content=message['attachment']['payload']['url']))
                                elif message['attachment']['type'] == 'template':
                                    if message['attachment']['payload']['template_type'] == 'button':
                                        buttons = message['attachment']['payload']['buttons']
                                        response.append(dict(**reply_params,
                                                             type='text',
                                                             content=message['attachment']['payload']['text']))

                                    elif message['attachment']['payload']['template_type'] == 'media':
                                        buttons = message['attachment']['payload']['elements'][0]['buttons']
                                        response.append(dict(**reply_params,
                                                             type='image',
                                                             content=message['attachment']['payload']['elements'][0][
                                                                 'url']))
                                    for button in buttons:
                                        response.append(dict(**reply_params,
                                                             type='button',
                                                             content=button['title'],
                                                             url=button['url']))

                if 'set_attributes' in service_response:
                    if 'user_input_text' in service_response['set_attributes']:
                        response.append(dict(**reply_params,
                                             type='text',
                                             content=service_response['set_attributes']['user_input_text']))

                if save_user_input or save_text_reply:
                    session_finish = 'true'

                # Refresh user_channel
                user_channel = self.get_user_channel(dict(id=user_channel['id']))

            if len(response) == 0:
                # Get bot default session:
                service_response = self.get_bot_session(user_id, bot_id, session_type='default')
                return JsonResponse(dict(response=[]))
        except Exception as e:
            # Get bot default session:
            service_response = self.get_bot_session(user_id, bot_id, session_type='default')
            return JsonResponse(dict(response=[]))

        return JsonResponse(dict(response=response))

    def get_user_channel(self, params):
        url_params = '?detail=True'
        for key, value in params.items():
            url_params += '&{0}={1}'.format(key, value)

        user_channel = requests.get(
            os.getenv("CONTENT_MANAGER_API") + '/messenger_users_channels/' + url_params).json()

        if 'count' in user_channel and user_channel['count'] > 0:
            return user_channel['results'][0]

        return False

    def get_user_data_attribute(self, user_id, name, default=False):

        endpoint = os.getenv("CONTENT_MANAGER_API") + '/messenger_users_data/'
        url_params = '?user_id={0}&attribute_name={1}'.format(user_id, name)

        service_response = requests.get(endpoint + url_params).json()
        if 'count' in service_response and service_response['count'] > 0:
            return service_response['results'][0]['data_value']

        return default

    def create_associate_user_attribute(self, user_id, data_key, data_value):
        endpoints = dict(
            create_user_data=os.getenv("CONTENT_MANAGER_DOMAIN") + '/chatfuel/create_messenger_user_data/',
            entities_add_attribute=os.getenv("CONTENT_MANAGER_API") + '/entities/add_attributes/',
            attribute=os.getenv("CONTENT_MANAGER_API") + '/attributes/'
        )

        # Crear el atributo si no existe
        attribute = requests.post(endpoints['attribute'], dict(name=data_key)).json()
        attribute_id = attribute['data']['id']

        # Asocial el atributo al usuario Encargado/Profesional
        requests.post(endpoints['entities_add_attribute'], json=[dict(entity=5, attributes=[attribute_id]),
                                                                 dict(entity=4, attributes=[attribute_id])])

        # Agregar el atributo al usuario
        requests.post(endpoints['create_user_data'], dict(data_key=data_key,
                                                          user_id=user_id,
                                                          data_value=data_value,
                                                          attribute_id=attribute_id))

    def get_bot_session(self, user_id, bot_id, session_type):
        endpoints = dict(
            bot_sessions=os.getenv("CONTENT_MANAGER_API") + '/bot_sessions/',
            get_session=os.getenv("CONTENT_MANAGER_DOMAIN") + '/chatfuel/get_session/'
        )
        # get the session id defaults to 0
        session = 0
        url_params = '?bot_id={0}&session_type={1}'.format(bot_id, session_type)
        service_response = requests.get(endpoints['bot_sessions'] + url_params).json()

        if 'count' in service_response and service_response['count'] > 0 and 'session_id' in \
                service_response['results'][0]:
            session = int(service_response['results'][0]['session_id'])

        # get the session
        service_params = dict(user_id=user_id, session=session)
        return requests.post(endpoints['get_session'], data=service_params).json()

    def create_interaction(self, bot_id, user_id, name):
        endpoints = dict(
            interaction=os.getenv("CONTENT_MANAGER_API") + '/interactions/',
            user_interaction=os.getenv("CONTENT_MANAGER_API") + '/user_interactions/'
        )
        # fetches the id of the interaction
        bot_interaction = requests.post(endpoints['interaction'], dict(name=name)).json()

        if 'data' in bot_interaction:
            # creates the interaction
            requests.post(endpoints['user_interaction'], dict(bot_id=bot_id,
                                                              user=user_id,
                                                              interaction=bot_interaction['data']['id'],
                                                              value=0,
                                                              created_at=timezone.now(),
                                                              updated_at=timezone.now()))
