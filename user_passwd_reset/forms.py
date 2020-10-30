from django import forms
from django.core import validators

class EmailSendForm(forms.Form):
    email = forms.EmailField(label="Email", validators=[validators.EmailValidator])

    def __init__(self, *args, **kwargs):
        super(EmailSendForm, self).__init__(*args, **kwargs)

        for field_name,field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def is_valid(self):
         result = super().is_valid()
         for x in (self.fields if '__all__' in self.errors else self.errors):
             attrs = self.fields[x].widget.attrs
             attrs.update({'class': attrs.get('class', '') + ' is-invalid'})
         return result

class PasswordResetForm(forms.Form):
    password = forms.CharField(label="Ingrese su nueva clave", widget=forms.PasswordInput(render_value=True), validators=[validators.MinLengthValidator(6, 'La clave debe tener al menos 6 caracteres')])
    password_confirm = forms.CharField(label="Confirme su nueva clave",widget=forms.PasswordInput(render_value=True),validators=[validators.MinLengthValidator(6, 'La clave debe tener al menos 6 caracteres')])

    def clean(self):
        pass1 = self.cleaned_data.get('password')
        pass2 = self.cleaned_data.get('password_confirm')

        if pass1 and pass1 != pass2:
            self.add_error('password_confirm','La clave no coincide')

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

        for field_name,field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def is_valid(self):
         result = super().is_valid()
         for x in (self.fields if '__all__' in self.errors else self.errors):
             attrs = self.fields[x].widget.attrs
             attrs.update({'class': attrs.get('class', '') + ' is-invalid'})
         return result
