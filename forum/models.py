import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from vote.models import VoteModel


def user_directory_path(instance, filename):
    return 'user{0}/{1}'.format(instance.user.id, filename)


class LikeManager(models.Manager):
    def create_like(self, user, obj, action='up-vote'):
        try:
            like = self.get(user=user)
            if like.is_active and action == 'down-vote':
                like.is_active = False
                obj.total_likes -= 1
            elif not like.is_active and action == 'up-vote':
                like.is_active = True
                obj.total_likes += 1
            like.save(update_fields=['is_active'])
        except Like.DoesNotExist:
            like = self.create(user=user)
            if action == 'like':
                obj.total_likes += 1
            else:
                like.is_active = False
            like.save()
            obj.likes.add(like)

        obj.save(update_fields=['total_likes'])
        return like


class ProfileManager(models.Manager):

    # TODO: Порефакторь это
    @staticmethod
    def update_profile_and_user(user, cleaned_data):
        user_fields_to_update, profile_fields_to_update = [], []
        profile = Profile.objects.get(user=user.id)
        user = User.objects.get(pk=user.id)
        username = cleaned_data.get('login', False)
        first_name = cleaned_data.get('first_name', False)
        last_name = cleaned_data.get('last_name', False)
        email = cleaned_data.get('email', False)
        bio = cleaned_data.get('bio', False)
        avatar = cleaned_data.get('avatar', False)
        if username:
            user_fields_to_update.append('username')
            user.username = username
        if first_name:
            user_fields_to_update.append('first_name')
            user.first_name = first_name
        if last_name:
            user_fields_to_update.append('last_name')
            user.last_name = last_name
        if email:
            user_fields_to_update.append('email')
            user.email = email
        if bio:
            profile_fields_to_update.append('bio')
            profile.bio = bio
        if avatar:
            profile_fields_to_update.append('avatar')
            profile.avatar = avatar

        if user_fields_to_update:
            user.save(update_fields=user_fields_to_update)
        if profile_fields_to_update:
            profile.save(update_fields=profile_fields_to_update)
        user_fields_to_update.extend(profile_fields_to_update)
        if user_fields_to_update:
            notification = Notification.objects.create(user=user, type='NEW', title='Profile updated',
                                                       text='You have updated {}.'.format(
                                                           (', '.join(user_fields_to_update)).replace('_', ' ')))
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
    def create_answer(self, user, question, text, vote_score=0):
        answer = self.create(user=user, question=question, text=text, vote_score=vote_score)
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
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=15)
    total = models.IntegerField(default=1)

    def __str__(self):
        return self.text


class Like(models.Model):
    objects = LikeManager()
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, models.SET(13))
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class Question(models.Model):
    objects = QuestionManager()

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,
                             models.SET(13))
    title = models.CharField(max_length=50)
    created = models.DateTimeField(default=datetime.datetime.now)
    text = models.CharField(max_length=500)
    tags = models.ManyToManyField(Tag)
    total_answers = models.IntegerField(default=0)
    likes = models.ManyToManyField(Like)
    total_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.SET(13))
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    objects = AnswerManager()
    created = models.DateTimeField(default=datetime.datetime.now)
    likes = models.ManyToManyField(Like)
    total_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.question.title


class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.SET(13))
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
