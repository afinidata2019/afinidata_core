# Generated by Django 2.2.10 on 2020-04-27 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0012_permission_add_code_to_company'),
        ('app', '0007_usergroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='codes',
            field=models.ManyToManyField(through='app.UserGroup', to='groups.Code'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(through='app.UserGroup', to='groups.Group'),
        ),
    ]