# Generated by Django 3.2.2 on 2021-06-29 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policyengine', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='governance_process_url',
            field=models.URLField(blank=True, max_length=100),
        ),
    ]
