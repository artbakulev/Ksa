from django.urls import path

from forum.views import index_view, registration_auth_view, profile_view, auth_view, logout_view, create_question_view, \
    question_view, profile_edit_view, vote_view

urlpatterns = [
    path('ajax_urls/vote/', vote_view, name='vote'),
    path('questions/<int:question_id>/', question_view, name='question'),
    path('create_question/', create_question_view, name='create_question'),
    path('logout/', logout_view, name='logout'),
    path('profile/edit/', profile_edit_view, name='profile_view'),
    path('profile/', profile_view, name='profile'),
    path('auth/', auth_view, name='auth'),
    path('registration/', registration_auth_view, name='registration'),
    path('<int:page>', index_view, name='index_page'),
    path('', index_view, name='index'),
]
