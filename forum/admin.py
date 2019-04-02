from django.contrib import admin

from forum.models import Question, Answer, Notification, Tag

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Notification)
admin.site.register(Tag)
