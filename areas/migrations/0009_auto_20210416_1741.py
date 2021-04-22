# Generated by Django 2.2.13 on 2021-04-16 23:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('areas', '0008_auto_20200909_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='area',
            name='topic',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='topics.Topic'),
        ),
        migrations.DeleteModel(
            name='Topic',
        ),
    ]