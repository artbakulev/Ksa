# Generated by Django 2.1.7 on 2019-03-11 15:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0006_auto_20190311_1536'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='user_profile',
            new_name='user',
        ),
    ]