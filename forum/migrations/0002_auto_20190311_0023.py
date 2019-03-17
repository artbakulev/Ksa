# Generated by Django 2.1.7 on 2019-03-11 00:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_of_notification', models.CharField(choices=[('ERR', 'Error'), ('NEW', 'New event'), ('ADM', 'Tech message')], default='ADM', max_length=3)),
                ('title_of_notification', models.CharField(max_length=15)),
                ('text_of_notification', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(upload_to='images/users')),
            ],
        ),
        migrations.AlterField(
            model_name='answer',
            name='User',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='question',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='question',
            name='tag1',
            field=models.CharField(default='', max_length=15),
        ),
        migrations.AlterField(
            model_name='question',
            name='tag2',
            field=models.CharField(default='', max_length=15),
        ),
        migrations.AlterField(
            model_name='question',
            name='tag3',
            field=models.CharField(default='', max_length=15),
        ),
        migrations.AlterField(
            model_name='question',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notification',
            name='user_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.UserProfile'),
        ),
    ]
