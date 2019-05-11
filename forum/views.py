from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from forum.forms import AnswerForm, EditProfileForm, RegistrationForm
from forum.models import Question, Notification, Answer, Tag, Profile, Like
from forum.scripts.paginator import make_paginator


def index_view(request, page=1):
    if request.GET.get('popular') is not None:
        sort_key = '-total_likes'
    elif request.GET.get('answered') is not None:
        sort_key = '-total_answers'
    else:
        sort_key = '-created'
    questions = Question.objects.order_by(sort_key)
    context = make_paginator(questions, page, 6)
    if context.get('error') is not None:
        raise context['error']
    context['questions'], context['tags'] = context['page'], Tag.objects.order_by('-total')[:5]
    return render(request, 'forum/index.html', context=context)


@transaction.atomic
def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        context = {'form': form}
        if not form.is_valid():
            return render(request, 'forum/registration.html', context=context)

        username, email, password = form['username'].value(), form['email'].value(), form['password'].value()

        if User.objects.filter(username=username).exists():
            context.update({'error': 'Login "{}" already taken.'.format(username)})
            return render(request, 'forum/registration.html', context=context)

        if User.objects.filter(email=email).exists():
            context.update({'error': 'Email "{}" already taken.'.format(email)})
            return render(request, 'forum/registration.html', context=context)

        if form['password'].value() != form['repeated_password'].value():
            context.update({'error': 'Passwords are not the same.'})
            return render(request, 'forum/registration.html', context=context)

        user = User.objects.create_user(username=username, email=email, password=password,
                                        first_name=form['first_name'].value(),
                                        last_name=form['last_name'].value())
        if user is not None:
            user.save()
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            return redirect('index')
        else:
            context.update({'error': 'Server error. Try again.'})
            return render(request, 'forum/registration.html', context=context)

    return render(request, 'forum/registration.html', context={'form': RegistrationForm()})


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
                  {'questions': questions,
                   'notifications': notifications,
                   'number_of_questions': str(len(questions)),
                   'total_answers': str(total_answers)})


@login_required(login_url='/auth')
def profile_edit_view(request):
    context = {}
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES)
        if not form.is_valid():
            context.update({'error': 'Something wrond with data', 'form': EditProfileForm()})
            return render(request, 'forum/profile/edit.html', context=context)

        user = request.user
        Profile.objects.update_profile_and_user(user, form.cleaned_data)
        return redirect('/profile')
    form = EditProfileForm()
    context.update({'form': form})
    return render(request, 'forum/profile/edit.html', context=context)


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
    context = {}

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = Answer.objects.create_answer(user=request.user, question=question, text=form.cleaned_data['text'])
            answer.save()
            return redirect('.')
        else:
            context.update({'error': "Invalid answer's data"})

    if question is None:
        raise Http404

    answers = Answer.objects.filter(question=question).order_by('created')
    form = AnswerForm()
    context.update({'form': form, 'question': question, 'answers': answers})

    return render(request, 'forum/question/question.html', context=context)


def tag_view(request, tag_name, page=1):
    questions = Question.objects.filter(tags__text=tag_name).order_by('-created')
    context = make_paginator(questions, page, 6, '/tags/' + tag_name)
    context['questions'] = context['page']
    context.pop('page')
    context['tags'] = Tag.objects.order_by('-total')[:5]
    context['tag'] = tag_name
    return render(request, 'forum/tags_index.html', context=context)


def user_view(request, username):
    try:
        user = User.objects.get(username=username)
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


@login_required()
def vote_view(request):
    post = request.POST
    user = request.user
    try:
        vote_object, action, object_id = post['object'], post['action'], post['object_id']
        if vote_object == 'question':
            vote_object = Question.objects.get(pk=object_id)
        else:
            vote_object = Answer.objects.get(pk=object_id)
        Like.objects.create_like(user, instance=vote_object, object_id=object_id, action=action)
        return HttpResponse(vote_object.total_likes, status=200)
    except KeyError:
        return HttpResponse(status=400)
