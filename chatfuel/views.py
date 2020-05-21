from instances.models import InstanceAssociationUser, Instance, AttributeValue, PostInteraction
from django.views.generic import View, CreateView, TemplateView, UpdateView
from articles.models import Article, Interaction as ArticleInteraction
from groups.models import Code, AssignationMessengerUser
from messenger_users.models import User as MessengerUser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from messenger_users.models import User, UserData
from django.http import JsonResponse, Http404
from dateutil import relativedelta, parser
from attributes.models import Attribute
from groups import forms as group_forms
from django.utils import timezone
from datetime import datetime
from chatfuel import forms
import random
import boto3
import os


''' MESSENGER USERS VIEWS '''


@method_decorator(csrf_exempt, name='dispatch')
class CreateMessengerUserView(CreateView):
    model = User
    fields = ('channel_id', 'bot_id', 'first_name', 'last_name')

    def form_valid(self, form):
        form.instance.last_channel_id = form.data['channel_id']
        form.instance.username = form.data['channel_id']
        form.instance.backup_key = form.data['channel_id']
        user = form.save()
        return JsonResponse(dict(set_attributes=dict(user_id=user.pk, request_status='done'), messages=[]))

    def form_invalid(self, form):
        user_set = User.objects.filter(channel_id=form.data['channel_id'])
        if user_set.count() > 0:
            return JsonResponse(dict(set_attributes=dict(user_id=user_set.last().pk,
                                                         request_status='error', request_message='User exists'),
                                     messages=[]))

        return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                     request_message='Invalid params'), messages=[]))


@method_decorator(csrf_exempt, name='dispatch')
class CreateMessengerUserDataView(CreateView):
    model = UserData
    fields = ('user', 'data_key', 'data_value')

    def form_valid(self, form):
        form.save()
        return JsonResponse(dict(set_attributes=dict(request_status='done'), messages=[]))

    def form_invalid(self, form):
        return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                     request_message='Invalid params'), messages=[]))



@method_decorator(csrf_exempt, name='dispatch')
class GetInitialUserData(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid Method'),
                                 messages=[]))

    def post(self, request):
        form = forms.UserForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid data.'),
                                     messages=[]))

        attributes = dict()

        for item in form.cleaned_data['user_id'].userdata_set.all():
            attributes[item.data_key] = item.data_value

        return JsonResponse(dict(set_attributes=attributes))


''' INSTANCES VIEWS '''


@method_decorator(csrf_exempt, name='dispatch')
class GetInstancesByUserView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid Method'),
                                 messages=[]))

    def post(self, request):
        form = forms.GetInstancesForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid data.'),
                                     messages=[]))

        label = "Choice your instance: "
        try:
            if form.data['label']:
                label = form.data['label']
        except:
            pass
        user = MessengerUser.objects.get(id=int(form.data['user']))
        replies = [dict(title=item.name, set_attributes=dict(instance=item.pk, instance_name=item.name)) for item in
                   user.get_instances()]

        return JsonResponse(dict(
            set_attributes=dict(request_status='done'),
            messages=[
                dict(
                    text=label,
                    quick_replies=replies
                )
            ]
        ))


@csrf_exempt
def create_instance(request):

    if request.method == 'GET':
        return JsonResponse(dict(
            set_attributes=dict(request_status='error', request_error='Invalid Method'),
            messages=[]
        ))

    form = forms.InstanceModelForm(request.POST)

    if not form.is_valid():
        return JsonResponse(dict(
            set_attributes=dict(request_status='error', request_error='Invalid Params'),
            messages=[]
        ))

    new_instance = form.save()
    assignation = InstanceAssociationUser.objects.create(user_id=form.data['user_id'], instance=new_instance)

    return JsonResponse(dict(
        set_attributes=dict(
            request_status='done',
            instance=new_instance.pk,
            instance_name=new_instance.name,
            instance_assignation_id=assignation.pk
        ),
        messages=[]
    ))


@method_decorator(csrf_exempt, name='dispatch')
class GetInstanceAttributeView(TemplateView):
    template_name = 'chatfuel/form.html'

    def get_context_data(self, **kwargs):
        c = super(GetInstanceAttributeView, self).get_context_data()
        c['form'] = forms.GetInstanceAttributeValue(None)
        return c

    def post(self, request, *args, **kwargs):
        form = forms.GetInstanceAttributeValue(self.request.POST)

        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params'),
                                     messages=[]))

        instance = Instance.objects.get(id=form.data['instance'])
        attributes = instance.entity.attributes.filter(name=form.data['attribute'])

        if not attributes.count() > 0:
            return JsonResponse(dict(set_attributes=dict(
                request_status='error',
                request_error='Entity of instance has not attribute with name %s.' % form.data['attribute']),
                                     messages=[]))

        attribute = Attribute.objects.get(name=form.data['attribute'])
        instance_attributes = AttributeValue.objects.filter(attribute=attribute, instance=instance)

        if not instance_attributes.count() > 0:
            return JsonResponse(dict(set_attributes=dict(
                request_status='error',
                request_error='Instance has not values with attribute: %s.' % form.data['attribute']),
                messages=[]))

        return JsonResponse(
            dict(set_attributes={
                'request_status': 'done',
                form.data['attribute']: instance_attributes.last().value
            },
                 messages=[])
        )


@method_decorator(csrf_exempt, name='dispatch')
class ChangeInstanceNameView(TemplateView):
    template_name = 'chatfuel/form.html'

    def get_context_data(self, **kwargs):
        c = super(ChangeInstanceNameView, self).get_context_data()
        c['form'] = forms.ChangeNameForm(None)
        print(c['form'])
        return c

    def post(self, request, *args, **kwargs):

        form = forms.ChangeNameForm(self.request.POST)

        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(
                request_status='error',
                request_error='Invalid Params.'
            ), messages=[]))

        instance = Instance.objects.get(id=form.data['instance'])
        instance.name = form.data['name']
        response = instance.save()

        return JsonResponse(dict(set_attributes=dict(
            request_status='done',
            request_message="name for instance has been changed.",
            instance_name=instance.name
        ), messages=[]))


''' CODE VIEWS '''


@method_decorator(csrf_exempt, name='dispatch')
class VerifyCodeView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse(dict(request_status='error', request_error='Invalid Method'))

    def post(self, request):
        form = forms.VerifyCodeForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_error='Invalid params'),
                                     messages=[]))

        code = Code.objects.get(code=form.data['code'])

        return JsonResponse(dict(set_attributes=dict(request_status='done', request_code=code.code,
                                                     request_code_group=code.group.name),
                                 messages=[]))


@method_decorator(csrf_exempt, name='dispatch')
class ExchangeCodeView(TemplateView):
    template_name = 'groups/code_form.html'

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        form = group_forms.ExchangeCodeForm(request.POST)

        if form.is_valid():
            user = form.cleaned_data['messenger_user_id']
            code = form.cleaned_data['code']
            changes = AssignationMessengerUser.objects.filter(messenger_user_id=user.pk)
            print(changes)
            if not changes.count() > 0:
                exchange = AssignationMessengerUser.objects.create(messenger_user_id=user.pk, group=code.group,
                                                                   code=code)
                code.exchange()
                return JsonResponse(dict(set_attributes=dict(request_status='done'), messages=[]))
            else:
                return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                             request_error='User be in group'), messages=[]))
        else:
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='User ID or code wrong'), messages=[]))


@method_decorator(csrf_exempt, name='dispatch')
class CreateInstanceAttributeView(CreateView):
    model = AttributeValue
    template_name = 'chatfuel/form.html'
    fields = ('instance', 'value', 'attribute')

    def get(self, request, *args, **kwargs):
        raise Http404

    def get_form(self, form_class=None):
        form = super(CreateInstanceAttributeView, self).get_form(form_class=None)
        form.fields['attribute'].to_field_name = 'name'
        return form

    def form_valid(self, form):

        if not form.instance.instance.entity.attributes.filter(id=form.instance.attribute.pk):
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Attribute not in instance'), messages=[]))

        attribute_value = form.save()

        return JsonResponse(dict(set_attributes=dict(
            set_attributes=dict(request_status='done', request_attribute_value_id=attribute_value.pk),
            messages=[]
        )))

    def form_invalid(self, form):
        return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                     request_error='Invalid params'), messages=[]))

    def get(self, request, *args):
        raise Http404


''' INTERACTION VIEWS '''


@method_decorator(csrf_exempt, name='dispatch')
class CreateInstanceInteractionView(CreateView):
    template_name = 'chatfuel/form.html'
    form_class = forms.InstanceInteractionForm

    def form_valid(self, form):
        form.instance.post_id = form.data['post_id']
        form.instance.created_at = timezone.now()
        interaction = form.save()

        if not interaction:
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Invalid params'), messages=[]))

        return JsonResponse(dict(set_attributes=dict(request_status='done',
                                                     request_interaction_id=interaction.pk),
                                 messages=[]))

    def form_invalid(self, form):
        return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                     request_error='Invalid params'), messages=[]))


''' CHILDREN '''

# FIX LATER, maybe not necessary in a future


@method_decorator(csrf_exempt, name='dispatch')
class GetFavoriteChildView(View):

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):

        form = forms.UserForm(request.POST)
        day_first = True

        if 'en' in form.data:
            if form.data['en'] == 'true':
                day_first = False

        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Invalid params',
                                                         favorite_request_error='invalid params'), messages=[]))

        user = form.cleaned_data['user_id']
        instances = user.get_instances()
        children = instances.filter(entity_id=1)

        if not children.count() > 0:
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='User has not children',
                                                         favorite_request_error='User has not children'), messages=[]))

        if children.count() == 1:
            birthdays = children.first().attributevalue_set.filter(attribute__name='birthday')
            birth = None

            if not birthdays.count() > 0:
                return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                             request_error='Unique child has not birthday',
                                                             favorite_request_error='Unique child has not birthday'),
                                         messages=[]))

            birth = birthdays.last().value

            return JsonResponse(dict(set_attributes=dict(request_status='done',
                                                         favorite_instance=children.first().pk,
                                                         favorite_instance_name=children.first().name,
                                                         favorite_birthday=birth), messages=[]))
        dates = set()
        for child in children:
            child_birthdays = child.attributevalue_set.filter(attribute__name='birthday')
            if child_birthdays.count() > 0:
                dates.add(child_birthdays.last().pk)

        print(dates)

        if not len(dates) > 0:
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_error='Neither child has birthday property',
                                                         favorite_request_error='Neither child has birthday property'),
                                     messages=[]))

        registers = AttributeValue.objects.filter(id__in=dates)

        favorite = dict(id=registers.first().instance_id, value=parser.parse(registers.first().value,
                                                                             dayfirst=day_first))

        for register in registers:
            print(register.value)
            register.value = parser.parse(register.value, dayfirst=day_first)
            print(register.value)
            if register.value > favorite['value']:
                favorite = dict(id=register.instance_id, value=register.value)

        attributes= dict(
                request_status='done',
                favorite_instace=favorite['id'],
                favorite_instance_name=Instance.objects.get(id=favorite['id']).name,
                favorite_birthday=favorite['value'].strftime('%d/%m/%Y')\
                    if day_first else favorite['value'].strftime('%m/%d/%Y')
            )

        return JsonResponse(dict(
            set_attributes=attributes,
            messages=[]
        ))


@method_decorator(csrf_exempt, name='dispatch')
class GetLastChildView(View):

    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        form = forms.UserForm(self.request.POST)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(
                request_status='error',
                request_error='Invalid params.'
            ), messages=[]))

        instances = form.cleaned_data['user_id'].get_instances()
        children = instances.filter(entity_id=1).order_by('id')

        if not children.count() > 0:
            return JsonResponse(dict(set_attributes=dict(
                request_status='error',
                request_error='User has not children.'
            ), messages=[]))

        attributes = dict(
            instance=children.last().pk,
            instance_name=children.last().name,
            favorite_instance=children.last().pk,
            favorite_instance_name=children.last().name,
            request_status='done'
        )

        if children.last().attributevalue_set.filter(attribute__name='birthday'):
            attributes['birthday'] = children.last().attributevalue_set.filter(attribute__name='birthday').\
                last().value
            attributes['favorite_birthday'] = children.last().attributevalue_set.filter(attribute__name='birthday'). \
                last().value

        return JsonResponse(dict(set_attributes=attributes, messages=[]))


''' ARTICLES '''


@method_decorator(csrf_exempt, name='dispatch')
class GetArticleView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request, *args, **kwargs):
        form = forms.UserArticleForm(request.POST)
        articles = Article.objects.all().only('id', 'name', 'min', 'max', 'preview', 'thumbnail')
        article = articles[random.randrange(0, articles.count())]
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(
                request_status='error',
                request_error='Invalid params.'
            ), messages=[]))
        instances = form.cleaned_data['user_id'].get_instances().filter(entity_id=1)
        if not instances.count() > 0:
            new_interaction = ArticleInteraction.objects\
                .create(user_id=form.data['user_id'], article=article, type='sent')
            print(new_interaction)
            return JsonResponse(dict(set_attributes=dict(
                request_status='done',
                article_id=article.pk,
                article_name=article.name,
                article_content=("%s/articles/%s/?licence=%s" % (os.getenv('CM_DOMAIN_URL'), article.pk,
                                                                 form.cleaned_data['licence'])),
                article_preview=article.preview,
                article_thumbail=article.thumbnail,
                article_instance="false",
                article_instance_name="false"
            ), messages=[]))
        birthdays = []
        for instance in instances:
            birthday_list = instance.attributevalue_set.filter(attribute__name='birthday')
            if birthday_list.count() > 0:
                try:
                    valid = parser.parse(birthday_list.last().value)
                    if valid:
                        birthdays.append(birthday_list.last())
                except:
                    pass
        print(birthdays)
        random_number = random.randrange(0, len(birthdays))
        date = birthdays[random_number]
        rel = relativedelta.relativedelta(datetime.now(), parser.parse(date.value))
        months = (rel.years * 12) + rel.months
        print(months)
        filter_articles = articles.filter(min__lte=months, max__gte=months)
        if not filter_articles.count() > 0:
            if not articles.count() > 0:
                return JsonResponse(dict(set_attributes=dict(
                    request_status='error',
                    request_error='Articles not exist.'
                ), messages=[]))
        else:
            article = filter_articles[random.randrange(0, filter_articles.count())]
            new_interaction = ArticleInteraction.objects \
                .create(user_id=form.data['user_id'], article=article, type='sent')
            print(new_interaction)
        return JsonResponse(dict(
            set_attributes=dict(
                request_status='done',
                article_id=article.pk,
                article_name=article.name,
                article_content=("%s/articles/%s/?licence=%s" % (os.getenv('CM_DOMAIN_URL'), article.pk,
                                                                 form.cleaned_data['licence'])),
                article_preview=article.preview,
                article_thumbail=article.thumbnail,
                article_instance=date.instance.pk,
                article_instance_name=date.instance.name
            ), messages=[]
        ))


''' CHATFUEL UTILITIES '''


@method_decorator(csrf_exempt, name='dispatch')
class BlockRedirectView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request, *args, **kwargs):
        form = forms.BlockRedirectForm(self.request.POST or None)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='Error',
                                                         request_error='Next field not found.'),
                                     messages=[]))

        return JsonResponse(dict(
            redirect_to_blocks=[form.cleaned_data['next']]
        ))


@method_decorator(csrf_exempt, name='dispatch')
class ValidatesDateView(View):

    def get(self, request, *args, **kwargs):
        raise Http404('Not found')

    def post(self, request):
        form = forms.ValidatesDateForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(set_attributes=dict(request_status='error', request_message='Invalid params')))

        months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october',
                  'november', 'december']

        region = os.getenv('region')
        translate = boto3.client(service_name='translate', region_name=region, use_ssl=True)
        result = translate.translate_text(Text=form.data['date'],
                                          SourceLanguageCode="auto", TargetLanguageCode="en")
        try:
            if form.data['variant'] == 'true':
                date = parser.parse(result.get('TranslatedText'))
            else:
                date = parser.parse(result.get('TranslatedText'), dayfirst=True)
        except Exception as e:
            print(e)
            return JsonResponse(dict(set_attributes=dict(request_status='error',
                                                         request_message='Not a valid string date')))

        rel = relativedelta.relativedelta(datetime.now(), date)
        child_months = (rel.years * 12) + rel.months

        lang = form.data['locale'][0:2]
        month = months[date.month - 1]
        date_result = translate.translate_text(Text="%s %s, %s" % (month, date.day, date.year), SourceLanguageCode="en",
                                               TargetLanguageCode=lang)
        locale_date = date_result.get('TranslatedText')
        return JsonResponse(dict(set_attributes=dict(
            childDOB=date,
            locale_date=locale_date,
            childMonths=child_months,
            request_status='done',
            childYears=rel.years,
            childExcedMonths=rel.months
        )))
