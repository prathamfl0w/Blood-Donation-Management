# Generated by Django 5.2 on 2025-05-07 21:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_bloodrequest_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bloodrequest',
            name='user',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
