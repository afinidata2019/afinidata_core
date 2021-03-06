from instances.models import Instance, AttributeValue, PostInteraction
from user_sessions.models import Session, Field
from attributes.models import Attribute
from messenger_users.models import User
from articles.models import Article, Topic
from programs.models import Program
from groups.models import Code
from posts.models import Post
from django import forms


class SetSectionToInstance(forms.Form):
    instance = forms.ModelChoiceField(Instance.objects.all())
    value = forms.IntegerField()


class GetInstancesForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())
    label = forms.CharField(max_length=50, required=False)


class VerifyCodeForm(forms.Form):
    code = forms.ModelChoiceField(Code.objects.all(), to_field_name='code')


class InstanceModelForm(forms.ModelForm):
    user_id = forms.ModelChoiceField(queryset=User.objects.all().only('id'))

    class Meta:
        model = Instance
        fields = ('entity', 'name')


class InstanceAttributeValue(forms.ModelForm):
    instance = forms.ModelChoiceField(queryset=Instance.objects.all())

    class Meta:
        model = AttributeValue
        fields = ('attribute', 'value')


class GetInstanceAttributeValue(forms.Form):
    instance = forms.ModelChoiceField(queryset=Instance.objects.all())
    attribute = forms.ModelChoiceField(queryset=Attribute.objects.all(), to_field_name='name')


class ChangeNameForm(forms.Form):
    instance = forms.ModelChoiceField(queryset=Instance.objects.all())
    name = forms.CharField(max_length=30)


class InstanceInteractionForm(forms.ModelForm):
    post_id = forms.ModelChoiceField(queryset=Post.objects.all().only('id', 'name'))

    class Meta:
        model = PostInteraction
        fields = ('instance', 'type', 'value')


class UserForm(forms.Form):
    user_id = forms.ModelChoiceField(queryset=User.objects.all())
    en = forms.BooleanField(required=False)


class MessengerUserForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), to_field_name='last_channel_id')


class ReplaceUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'channel_id')


class BlockRedirectForm(forms.Form):
    next = forms.CharField(max_length=40)


class UserArticleForm(forms.Form):
    user_id = forms.ModelChoiceField(queryset=User.objects.all())
    licence = forms.CharField(max_length=30)
    en = forms.BooleanField(required=False)
    article = forms.ModelChoiceField(queryset=Article.objects.all().only('id'), required=False)


class ValidatesDateForm(forms.Form):
    date = forms.CharField(max_length=40)
    locale = forms.CharField(max_length=10)
    variant = forms.ChoiceField(choices=(('true', 'true'), ('false', 'false')))


class ArticleForm(forms.Form):
    article = forms.ModelChoiceField(queryset=Article.objects.all().only('id', 'name', 'thumbnail', 'text_content'))


class InstanceForm(forms.Form):
    instance = forms.ModelChoiceField(queryset=Instance.objects.all())
    program = forms.ModelChoiceField(queryset=Program.objects.all(), required=False)
    locale = forms.CharField(max_length=10, required=False)


class SessionFieldForm(forms.Form):
    session = forms.ModelChoiceField(queryset=Session.objects.all())
    position = forms.IntegerField()
    instance = forms.ModelChoiceField(queryset=Instance.objects.all())
    user_id = forms.ModelChoiceField(queryset=User.objects.all())


class SessionForm(forms.Form):
    instance = forms.ModelChoiceField(queryset=Instance.objects.all())
    user_id = forms.ModelChoiceField(queryset=User.objects.all())
    topics = forms.ModelMultipleChoiceField(queryset=Topic.objects.all(), to_field_name="name", required=False)
