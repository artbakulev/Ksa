import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from configuration import DELETED_USER


def user_directory_path(instance, filename):
    return 'user{0}/{1}'.format(instance.user.id, filename)


class LikeManager(models.Manager):
    def is_liked(self, user, object_id):
        try:
            like = self.filter(user=user).get(object_id=object_id)
            if like.is_active:
                return True
        except Like.DoesNotExist:
            pass
        return False

    def create_like(self, user, instance, object_id, action='up-vote'):
        try:
            like = self.filter(user=user).get(object_id=object_id)
            if like.is_active and action == 'down-vote':
                like.is_active = False
                instance.total_likes -= 1
            elif not like.is_active and action == 'up-vote':
                like.is_active = True
                instance.total_likes += 1
            like.save(update_fields=['is_active'])
        except Like.DoesNotExist:
            like = self.create(user=user, obj=instance, object_id=instance.id)
            if action == 'up-vote':
                instance.total_likes += 1
            else:
                like.is_active = False
            like.save()

        instance.save(update_fields=['total_likes'])
        return like


class ProfileManager(models.Manager):
    @staticmethod
    def update_profile_and_user(user, cleaned_data):
        user_fields, profile_fields = ['username', 'first_name', 'email'], ['bio', 'avatar']
        fields_to_update = {'user': [], 'profile': []}

        profile = Profile.objects.get(user=user.id)
        user = User.objects.get(pk=user.id)

        for key in user_fields:
            value = cleaned_data.get(key, False)
            if value:
                fields_to_update['user'].append(key)
                setattr(user, key, value)

        for key in profile_fields:
            value = cleaned_data.get(key, False)
            if value:
                fields_to_update['profile'].append(key)
                setattr(profile, key, value)

        user.save(update_fields=fields_to_update['user'])
        profile.save(update_fields=fields_to_update['profile'])

        fields_to_update = list(fields_to_update['user'] + fields_to_update['profile'])
        if fields_to_update:
            notification = Notification.objects.create(user=user, type='NEW', title='Profile updated',
                                                       text='You have updated {}.'.format(
                                                           (', '.join(fields_to_update)).replace('_', ' ')))
            notification.save()
        return user, profile


class QuestionManager(models.Manager):
    def create_question(self, **kwargs):
        user_id = kwargs['user']
        title = kwargs['title']
        text = kwargs['text']
        tags = TagManager.format_tags(kwargs['tags'])
        question = self.create(user=user_id, title=title, text=text)
        question.save()
        for tag in tags:
            current_tag = Tag.objects.create_or_update_tag(tag)
            question.tags.add(current_tag)
        return question


class AnswerManager(models.Manager):
    def create_answer(self, user, question, text, total_likes=0):
        answer = self.create(user=user, question=question, text=text, total_likes=total_likes)
        question = Question.objects.get(pk=question.id)
        question.total_answers += 1
        question.save(update_fields=['total_answers'])
        notification = Notification.objects.create(user=question.user, type='NEW', title='New answer',
                                                   text='New answer on question "{}"'.format(question.title))
        notification.save()

        return answer


class TagManager(models.Manager):
    @staticmethod
    def format_tags(tags):
        tags = tags[:3]
        while len(tags) < 3:
            tags.append(False)
        return tags

    # TODO: transaction.atomic, select_for_update
    def create_or_update_tag(self, tag):
        try:
            tag = self.get(text=tag)
            tag.total += 1
            tag.save(update_fields=['total'])
        except Tag.DoesNotExist:
            tag = self.create(text=tag, total=1)
            tag.save()
        return tag


class Profile(models.Model):
    objects = ProfileManager()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to=user_directory_path, default='/avatars/default_user.jpg')

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Tag(models.Model):
    objects = TagManager()
    text = models.CharField(max_length=15, unique=True)
    total = models.IntegerField(default=1)

    def __str__(self):
        return self.text


class Like(models.Model):
    objects = LikeManager()
    user = models.ForeignKey(User, models.SET(DELETED_USER))
    is_active = models.BooleanField(default=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    obj = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.user.username


class Question(models.Model):
    objects = QuestionManager()
    user = models.ForeignKey(User,
                             models.SET(DELETED_USER))
    title = models.CharField(max_length=50)
    created = models.DateTimeField(default=datetime.datetime.now)
    text = models.CharField(max_length=500)
    tags = models.ManyToManyField(Tag)
    total_answers = models.IntegerField(default=0)
    total_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Answer(models.Model):
    objects = AnswerManager()

    user = models.ForeignKey(User, models.SET(DELETED_USER))
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    created = models.DateTimeField(default=datetime.datetime.now)
    total_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.question.title


class Notification(models.Model):
    user = models.ForeignKey(User, models.SET(DELETED_USER))
    TYPE_OF_NOTIFICATIONS_CHOICES = (
        ('ERR', 'Error'),
        ('NEW', "New event"),
        ('ADM', "Tech message")
    )
    type = models.CharField(max_length=3, choices=TYPE_OF_NOTIFICATIONS_CHOICES)
    title = models.CharField(max_length=60)
    text = models.CharField(max_length=150)
    created = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.title
