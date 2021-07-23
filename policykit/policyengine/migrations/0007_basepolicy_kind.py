# Generated by Django 3.2.2 on 2021-07-23 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policyengine', '0006_remove_basepolicy_is_bundled'),
    ]

    operations = [
        migrations.AddField(
            model_name='basepolicy',
            name='kind',
            field=models.CharField(blank=True, choices=[('platform', 'platform'), ('constitution', 'constitution')], max_length=30),
        ),
    ]
