# Generated by Django 2.2.10 on 2020-05-05 16:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('instances', '0017_auto_20200406_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instancefeedback',
            name='area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='areas.Area'),
        ),
        migrations.AlterField(
            model_name='instancefeedback',
            name='instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instances.Instance'),
        ),
    ]
