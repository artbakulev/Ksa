import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from vote.models import VoteModel


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class QuestionManager(models.Manager):
    def create_question(self, **kwargs):
        user_id = kwargs['user']
        title = kwargs['title']
        text = kwargs['text']
        tags = TagManager.format_tags(kwargs['tags'])
        question = self.create(user=user_id, title=title, text=text, tag1=tags[0], tag2=tags[1], tag3=tags[2])
        question.save()
        for tag in tags:
            Tag.objects.create_or_update_tag(tag)
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


class Question(VoteModel, models.Model):
    objects = QuestionManager()

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,
                             models.SET(13))
    title = models.CharField(max_length=50)
    created = models.DateTimeField(default=datetime.datetime.now)
    text = models.CharField(max_length=500)
    tag1 = models.CharField(max_length=15, default='')
    tag2 = models.CharField(max_length=15, default='')
    tag3 = models.CharField(max_length=15, default='')
    total_answers = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Answer(VoteModel, models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.SET(13))
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    objects = AnswerManager()
    created = models.DateTimeField(default=datetime.datetime.now)

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


class Tag(models.Model):
    objects = TagManager()

    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=15)
    total = models.IntegerField(default=1)

    def __str__(self):
        return self.text
