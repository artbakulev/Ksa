# Generated by Django 2.1.7 on 2019-03-17 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0016_auto_20190312_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='text',
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name='notification',
            name='title',
            field=models.CharField(max_length=30),
        ),
    ]
