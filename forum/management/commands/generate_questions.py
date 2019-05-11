from random import randint

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils.datetime_safe import datetime
from faker import Faker

from forum.management.commands.logger import make_logger
from forum.management.commands.random_getter import get_random
from forum.models import Question, Tag, Like

fake = Faker()

fake.name()

OBJECTS_NUMBER = 10
MAX_LIKES_PER_ONE_QUESTION = 10
QUESTIONS_PER_ONE_GENERATION = 100


class Command(BaseCommand):
    DEBUG_MODE = False

    def add_arguments(self, parser):
        parser.add_argument('questions', type=int)

        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode',
        )

    def handle(self, *args, **options):
        logger = make_logger(options['debug'])
        fake = Faker()
        logger.info('Generating {} question...'.format(options['questions']))
        start_time = datetime.now().timestamp()
        total_questions = options['questions']
        i = 0
        while i < total_questions:
            users = get_random(User, OBJECTS_NUMBER + 1)
            tags = get_random(Tag, OBJECTS_NUMBER + 1)
            for j in range(QUESTIONS_PER_ONE_GENERATION):
                logger.info('Generate {} / {} question.'.format(i + 1, options['questions']))
                question = Question(user=users[randint(0, OBJECTS_NUMBER)], title=fake.text(max_nb_chars=50),
                                    text=fake.text(max_nb_chars=450, ext_word_list=None))
                question.save()
                for q in range(3):
                    tag = tags[randint(0, OBJECTS_NUMBER)]
                    tag.total += 1
                    tag.save(update_fields=['total'])
                    question.tags.add(tag)

                likes_total = randint(0, MAX_LIKES_PER_ONE_QUESTION)
                for i in range(likes_total):
                    like = Like.objects.create_like(user=users[randint(0, OBJECTS_NUMBER)], model=Question,
                                                    object_id=question.id)
                    like.save()
                question.total_likes = likes_total
                question.save(update_fields=['total_likes'])
                i += 1
        logger.info('Operation executed in {} seconds'.format(datetime.now().timestamp() - start_time))
