# Generated by Django 2.2.13 on 2020-08-07 18:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_sessions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='parent_session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_sessions.Session'),
        ),
    ]
