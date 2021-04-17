# Generated by Django 2.2.13 on 2021-04-16 23:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0004_interaction_instance_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
