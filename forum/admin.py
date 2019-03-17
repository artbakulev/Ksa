from django.contrib import admin

from forum.models import Question, Answer, Notification

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Notification)
