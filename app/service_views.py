from django.views.generic import CreateView, View, ListView
from django.contrib.auth.hashers import check_password
from instances.models import Instance, AttributeValue
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.core.validators import EmailValidator
from dateutil import relativedelta
from dateutil.parser import parse
from django.utils import timezone
from areas.models import Area
from posts.models import Post
import json
from app import (
    decorators,
    utilities,
    models,
    forms,
)


@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class SignUpView(CreateView):
    model = models.User
    fields = ('password', 'identifier')
    template_name = 'app/form.html'

    def get(self, request, *args, **kwargs):
        return HttpResponse('Unauthorized', status=403)

    def get_form(self, form_class=None):
        form = super(SignUpView, self).get_form()
        form.fields['identifier'].validators = [EmailValidator()]
        form.fields['password'].required = True
        return form

    def form_valid(self, form):
        user = form.save()
        if user:
            return JsonResponse(dict(status='done',
                                     data=dict(
                                         user_id=user.pk,
                                         user_identifier=user.identifier,
                                         token=utilities.generate_token(dict(user_id=user.pk)))))

    def form_invalid(self, form):
        return JsonResponse(dict(status='error', errors=json.loads(form.errors.as_json())))


@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class AnonLoginView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Unauthorized', status=403)

    def post(self, request):
        form = forms.AnonLoginForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(status='error', errors=json.loads(form.errors.as_json())))

        return JsonResponse(dict(status='done', data=dict(
            user_id=form.cleaned_data['identifier'].pk,
            token=utilities.generate_token(dict(user_id=form.cleaned_data['identifier'].pk))
        )))


@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Unauthorized', status=403)

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(status='error', errors=json.loads(form.errors.as_json())))

        checker = check_password(form.cleaned_data['password'], form.cleaned_data['identifier'].password)
        if not checker:
            return JsonResponse(dict(status='error', errors=dict(
                password=[dict(message='Invalid Password', code='required')]
            )))
        token = utilities.generate_token(dict(user_id=form.cleaned_data['identifier'].pk))
        return JsonResponse(dict(status='done', data=dict(
            first_name=form.cleaned_data['identifier'].first_name,
            last_name=form.cleaned_data['identifier'].last_name,
            user_id=form.cleaned_data['identifier'].pk,
            token=token
        )))


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(decorators.verify_token, name='dispatch')
class CreateInstanceView(CreateView):
    model = Instance
    fields = ('name', 'entity')

    def get(self, request, *args, **kwargs):
        return HttpResponse('Unauthorized', status=403)

    def form_valid(self, form):
        instance = form.save()
        instance.userinstanceassociation_set.create(user=self.request.user)
        return JsonResponse(dict(status='done', data=dict(
            instance_name=instance.name,
            instance_id=instance.pk,
            instance_type=instance.entity.name,
            token=utilities.generate_token(dict(user_id=self.request.user.pk))
        )))

    def form_invalid(self, form):
        return JsonResponse(dict(status='error', errors=json.loads(form.errors.as_json()),
                                 data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))))


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(decorators.verify_token, name='dispatch')
class GetInstancesView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Unauthorized', status=403)

    def post(self, request, *args, **kwargs):
        form = forms.GetInstancesForm(self.request.POST)
        if form.is_valid():
            instances = request.user.instances.filter(entity=form.cleaned_data['entity'])
            return JsonResponse(dict(status='done', data=dict(
                instances=[dict(id=i.pk, name=i.name) for i in instances],
                token=utilities.generate_token(dict(user_id=self.request.user.pk))
            )))

        return JsonResponse(dict(status='error', errors=json.loads(form.errors.as_json()),
                                 data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))))


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(decorators.verify_token, name='dispatch')
class AddAttributeToInstanceView(CreateView):
    model = AttributeValue
    fields = ('attribute', 'instance', 'value')
    template_name = 'app/form.html'

    def get_form(self, form_class=None):
        form = super(AddAttributeToInstanceView, self).get_form()
        form.fields['attribute'].to_field_name = 'name'
        return form

    def form_valid(self, form):
        instances = self.request.user.instances.filter(id=form.data['instance'])
        if not instances.count() > 0:
            return JsonResponse(dict(status='error',
                                     errors=dict(instance=[
                                         dict(message="This user has not this instance", code='required')
                                     ]),
                                     data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))
                                     ))
        instance = instances.last()
        attributes = instance.entity.attributes.filter(name=form.data['attribute'])
        if not attributes.count() > 0:
            return JsonResponse(dict(status='error',
                                     errors=dict(attribute=[
                                         dict(message="This attribute is not possible to add to instance",
                                              code='required')
                                     ]),
                                     data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))
                                     ))
        attribute = attributes.last()
        new_attr = instance.attributevalue_set.create(attribute=attribute, value=form.data['value'])
        if not new_attr:
            return JsonResponse(dict(status='error',
                                     errors=dict(value=[
                                         dict(message="Not possible added value to this attribute to instance",
                                              code='required')
                                     ]),
                                     data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))
                                     ))
        return JsonResponse(dict(status='done',
                                 data=dict(
                                     operation_id=new_attr.pk,
                                     token=utilities.generate_token(dict(user_id=self.request.user.pk)),
                                     attribute=new_attr.attribute.name,
                                     value=new_attr.value
                                 )))

    def form_invalid(self, form):
        return JsonResponse(dict(status='error', errors=json.loads(form.errors.as_json()),
                                 data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))))


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(decorators.verify_token, name='dispatch')
class AreaListView(ListView):
    model = Area

    def post(self, request, *args, **kwargs):
        results = self.get_queryset()
        return JsonResponse(dict(
            status='done',
            data=dict(
                areas=[dict(id=area.pk, name=area.name) for area in results],
                token=utilities.generate_token(dict(user_id=self.request.user.pk))
            )
        ))


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(decorators.verify_token, name='dispatch')
class GetPostsByAreaView(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.filter(status='published').only('id', 'name', 'min_range', 'max_range', 'thumbnail')

    def post(self, request, *args, **kwargs):
        form = forms.GetActivitiesForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(status='error', errors=json.loads(form.errors.as_json()),
                                     data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))))

        if not form.cleaned_data['instance'] in request.user.instances.all():
            return JsonResponse(dict(status='error', errors=dict(instance=[dict(message='User has not instance',
                                                                                code='required')]),
                                     data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))))

        limit = form.cleaned_data['instance'].get_attribute_values('birthday')

        if not limit:
            return JsonResponse(dict(status='error', errors=dict(birthday=[dict(message='instance has not birthday',
                                                                                code='required')]),
                                     data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))))

        date = parse(limit.value)
        rel = relativedelta.relativedelta(timezone.now(), date)
        months = (rel.years * 12) + rel.months

        posts = self.get_queryset().filter(area_id=form.data['area'], min_range__lte=months, max_range__gte=months)

        return JsonResponse(dict(status='done', data=dict(
            posts=[dict(id=post.pk, name=post.name, thumbnail=post.thumbnail, min=post.min_range, max=post.max_range)
                   for post in posts])))


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(decorators.verify_token, name='dispatch')
class GetPostView(View):

    def post(self, request, *args, **kwargs):
        form = forms.GetPostForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(status='error', errors=dict(post=[dict(message='Post not exist',
                                                                            code='required')]),
                                     data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))))
        return JsonResponse(dict(
            status='done', data=dict(post=dict(
                    id=form.cleaned_data['post'].pk,
                    name=form.cleaned_data['post'].name,
                    thumbnail=form.cleaned_data['post'].thumbnail,
                    content=form.cleaned_data['post'].content
                ),
                token=utilities.generate_token(dict(user_id=self.request.user.pk)))))


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(decorators.verify_token, name='dispatch')
class ExchangeCodeView(CreateView):
    model = models.UserGroup
    fields = ('code',)
    template_name = 'app/form.html'

    def get_form(self, form_class=None):
        form = super(ExchangeCodeView, self).get_form()
        form.fields['code'].to_field_name = 'code'
        return form

    def form_valid(self, form):
        print(form.cleaned_data['code'].group)
        form.instance.user = self.request.user
        form.instance.group = form.cleaned_data['code'].group
        exchange = form.save()
        print(exchange)
        return JsonResponse(dict(status='done', data=dict(
            group_name=exchange.group.name,
            operation_id=exchange.pk,
            token=utilities.generate_token(dict(user_id=self.request.user.pk))
        )))

    def form_invalid(self, form):
        return JsonResponse(dict(status='error', errors=json.loads(form.errors.as_json()),
                                 data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))))


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(decorators.verify_token, name='dispatch')
class VerifyGroups(View):

    def post(self, request, *args, **kwargs):
        print(request.user.groups.all())
        if not request.user.groups.all().count() > 0:
            return JsonResponse(dict(status='error',
                                     errors=dict(
                                         groups=[
                                            dict(
                                                message='User has not groups',
                                                code='required'
                                            )
                                         ]
                                     ),
                                     data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))))
        return JsonResponse(dict(
            status='done',
            data=dict(
                groups=[dict(id=group.pk, name=group.name) for group in request.user.groups.all()],
                token=utilities.generate_token(dict(user_id=self.request.user.pk))
            )
        ))


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(decorators.check_authorization, name='dispatch')
@method_decorator(decorators.verify_token, name='dispatch')
class VerifyAttributeView(View):

    def post(self, request, *args, **kwargs):
        form = forms.VerifyAttributeForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(status='error', errors=json.loads(form.errors.as_json()),
                                     data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))))

        attributes = form.cleaned_data['instance'].attributevalue_set.filter(attribute=form.cleaned_data['attribute'])

        if not attributes.count() > 0:
            return JsonResponse(dict(status='error',
                                     errors=dict(
                                         attribute=[dict(message='Instance has not attribute', code='required')]
                                     ),
                                     data=dict(token=utilities.generate_token(dict(user_id=self.request.user.pk)))))
        print(attributes)
        return JsonResponse(dict(status='done', data=dict(
            value=attributes.last().value, token=utilities.generate_token(dict(user_id=self.request.user.pk)))))
