from django.contrib import admin

from forum.models import Question, Answer, Notification, Tag, Profile, Like

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Notification)
admin.site.register(Tag)
admin.site.register(Profile)
admin.site.register(Like)
