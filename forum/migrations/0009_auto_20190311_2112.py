# Generated by Django 2.1.7 on 2019-03-11 21:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0008_auto_20190311_1547'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='user',
            new_name='User',
        ),
    ]
