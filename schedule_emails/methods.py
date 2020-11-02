import os
from core import settings
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def enviar_correo(asunto, template, recipients, data, attachment_file=None):
    image_path = os.path.join(settings.BASE_DIR, 'assets/images/afini_logo.png')
    image_name = 'afini_logo.png'

    context = {'image_name':image_name, 'data': data}
    html_content = render_to_string(template, context)
    reply_to = ['no-reply@afinidata.com']

    message = EmailMultiAlternatives(asunto,
    html_content,
    os.getenv('MAIL_USER'),
    to=recipients,
    reply_to=reply_to)

    if attachment_file is not None:
        message.attach_file(os.path.join(settings.BASE_DIR, attachment_file))

    message.attach_alternatives = (html_content, "text/html")
    message.content_subtype = "html"
    message.mixed_subtype = 'related'


    with open(image_path, mode='rb') as f:
        image = MIMEImage(f.read())
        message.attach(image)
        image.add_header('Content-ID',f"<{image_name}>")

    message.send()
