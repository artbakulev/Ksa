from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect

from forum.models import Question, Notification, Answer, Tag
from forum.scripts.paginator import make_paginator


def index_view(request, page=1):
    if request.GET.get('popular'):
        sort_key = '-vote_score'
    elif request.GET.get('answered'):
        sort_key = '-total_answers'
    else:
        sort_key = '-created'
    questions = Question.objects.order_by(sort_key)
    context = make_paginator(questions, page, 6)
    context['questions'] = context['page']
    context.pop('page')
    context['tags'] = Tag.objects.order_by('-total')[:5]

    return render(request, 'forum/index.html', context=context)


def registration_auth_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        if User.objects.filter(username=username).exists():
            return render(request, 'forum/registration.html', {'error': 'Login "{}" already taken.'.format(username)})
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            return render(request, 'forum/registration.html', {'error': 'Email "{}" already in use.'.format(email)})
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        password = request.POST['password']
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name,
                                        last_name=last_name)
        if user is not None:
            user.save()
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            return redirect('index')
        else:
            return render(request, 'forum/registration.html', {'error': 'Server error. Try again.'})
    return render(request, 'forum/registration.html')


def auth_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        return render(request, 'forum/auth.html', {'error': 'Login or/and password are incorrect. Try again.'})
    return render(request, 'forum/auth.html')


@login_required(login_url='/auth')
def logout_view(request):
    logout(request)
    return redirect('index')


@login_required(login_url='/auth/')
def profile_view(request):
    user = request.user
    questions = Question.objects.filter(user=user.id).order_by('created')
    total_answers = 0
    for question in questions:
        total_answers += question.total_answers
    notifications = Notification.objects.filter(user=user.id).order_by('-created')
    return render(request, 'forum/profile/profile.html',
                  {'user': user, 'is_authenticated': True, 'questions': questions, 'notifications': notifications,
                   'number_of_questions': str(len(questions)),
                   'total_answers': str(total_answers)})


@login_required(login_url='/auth')
def profile_edit_view(request):
    user = request.user
    if request.method == 'POST':
        post = request.POST
        new_login = post.get('login')
        new_email = post.get('email')
        new_avatar = post.get('avatar')

        if new_login or new_email:
            notification = Notification.objects.create(user_id=user.id, type='NEW', title='Credentials has changed')
            notification_text = 'You change your %s recently'
            user_to_update = User.objects.get(pk=user.id)
            if new_login and not new_email:
                user_to_update.username = new_login
                notification_text = notification_text % 'email'
                user_to_update.save(update_fields=['username'])
            elif new_email and not new_login:
                user_to_update.email = new_email
                notification_text = notification_text % 'login'
                user_to_update.save(update_fields=['email'])
            else:
                user_to_update.username = new_login
                user_to_update.email = new_email
                notification_text = notification_text % 'login and email'
                user_to_update.save(update_fields=['username', 'email'])

            notification.text = notification_text
            notification.save()
        return redirect('/profile')

    return render(request, 'forum/profile/edit.html')


@login_required(login_url='/auth')
def create_question_view(request):
    if request.method == 'POST':
        title = request.POST['title']
        tags = request.POST['tags'].split()
        text = request.POST['text']
        question = Question.objects.create_question(user=request.user, title=title, tags=tags, text=text)
        if question is not None:
            question.save()
            return redirect('../questions/{}'.format(question.id))
        return render(request, 'forum/question/create_question.html', {'error': 'Something went wrong. Try again.'})
    return render(request, 'forum/question/create_question.html')


def question_view(request, question_id):
    question = Question.objects.get(pk=question_id)
    if request.method == 'POST':
        post = request.POST

        if post.get('new_answer'):
            answer = Answer.objects.create_answer(user=request.user, question=question, text=post['new_answer'])
            answer.save()
            return redirect('.')
    if question is None:
        return HttpResponse(status=404)
    answers = Answer.objects.filter(question=question).order_by('-created')[:5]
    return render(request, 'forum/question/question.html',
                  {'question': question, 'answers': answers, })


def tag_view(request, tag_name, page=1):
    questions = Question.objects.filter(tag1=tag_name).union(Question.objects.filter(tag2=tag_name),
                                                             Question.objects.filter(
                                                                 tag3=tag_name))  # TODO: Refactor this
    context = make_paginator(questions, page, 6)
    context['questions'] = context['page']
    context.pop('page')
    context['tags'] = Tag.objects.order_by('-total')[:5]
    return render(request, 'forum/index.html', context=context)


def user_view(request, user_name):
    try:
        user = User.objects.get(username=user_name)
        questions = Question.objects.filter(user=user.id).order_by('created')
        total_answers = 0
        for question in questions:
            total_answers += question.total_answers
        return render(request, 'forum/profile/user_profile.html',
                      {'user': user, 'questions': questions,
                       'number_of_questions': str(len(questions)),
                       'total_answers': str(total_answers)})
    except User.DoesNotExist:
        return HttpResponse(status=404)


def vote_view(request):
    post = request.POST
    user = request.user
    if not user.is_authenticated:
        return HttpResponse(status=403)
    try:
        user_id = user.id
        vote_object = post['object']
        action = post['action']
        object_id = post['object_id']
        if vote_object == 'answer':
            vote_object = Answer.objects.get(pk=object_id)
            if action == 'up-vote':
                vote_object.votes.up(user_id)
            elif action == 'down-vote':
                vote_object.votes.down(user_id)

        elif vote_object == 'question':
            vote_object = Question.objects.get(pk=object_id)
            if action == 'up-vote':
                vote_object.votes.up(user_id)
            elif action == 'down-vote':
                vote_object.votes.down(user_id)
        return HttpResponse(vote_object.votes.count(), status=200)
    except KeyError:
        return HttpResponse(status=400)
