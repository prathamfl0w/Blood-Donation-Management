# Generated by Django 5.2 on 2025-04-16 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_bloodrequest_options_bloodrequest_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('user', 'User')], default='user', max_length=10),
        ),
    ]
