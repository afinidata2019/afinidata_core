# Generated by Django 2.2.13 on 2020-08-03 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='campaign',
            field=models.BooleanField(default=False),
        ),
    ]
