import datetime

from django.contrib.auth.models import User
from django.db import models

from vote.models import VoteModel


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


class Question(VoteModel, models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,
                             models.CASCADE)  # TODO: Переделай чтобы не удалялись все вопросы при удаление пользователя
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
    user = models.ForeignKey(User, models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    objects = AnswerManager()
    created = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.question.title


class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.CASCADE)
    TYPE_OF_NOTIFICATIONS_CHOICES = (
        ('ERR', 'Error'),
        ('NEW', "New event"),
        ('ADM', "Tech message")
    )
    type = models.CharField(max_length=3, choices=TYPE_OF_NOTIFICATIONS_CHOICES)
    title = models.CharField(max_length=30)
    text = models.CharField(max_length=60)
    created = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.title
