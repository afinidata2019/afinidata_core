# Generated by Django 2.2.13 on 2021-04-16 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('languages', '0013_language_auto_translate'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='label',
            field=models.CharField(max_length=20, null=True, unique=True),
        ),
    ]
