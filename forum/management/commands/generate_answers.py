from random import randint

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils.datetime_safe import datetime
from faker import Faker

from forum.management.commands.logger import make_logger
from forum.management.commands.random_getter import get_random
from forum.models import Question, Like, Answer

fake = Faker()

fake.name()

OBJECTS_NUMBER = 10
MAX_LIKES_PER_ONE_ANSWER = 10
ANSWERS_PER_ONE_GENERATION = 100


class Command(BaseCommand):
    DEBUG_MODE = False

    def add_arguments(self, parser):
        parser.add_argument('answers', type=int)

        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode',
        )

    def handle(self, *args, **options):
        logger = make_logger(options['debug'])
        fake = Faker()
        logger.info('Generating {} answers...'.format(options['answers']))
        start_time = datetime.now().timestamp()
        total_questions = options['answers']
        i = 0
        while i < total_questions:
            users = get_random(User, OBJECTS_NUMBER + 1)
            questions = get_random(Question, OBJECTS_NUMBER + 1)
            likes = get_random(Like, 2 * OBJECTS_NUMBER + 1)
            for j in range(ANSWERS_PER_ONE_GENERATION):
                logger.info('Generate {} / {} answer.'.format(i + 1, options['answers']))
                question = questions[randint(0, OBJECTS_NUMBER)]
                question.total_answers += 1
                question.save(update_fields=['total_answers'])
                total_likes = randint(0, MAX_LIKES_PER_ONE_ANSWER)

                answer = Answer.objects.create_answer(user=users[randint(0, OBJECTS_NUMBER)], question=question,
                                                      text=fake.text(max_nb_chars=450, ext_word_list=None),
                                                      total_likes=total_likes)
                answer.save()
                for q in range(total_likes):
                    answer.likes.add(likes[randint(0, 2 * OBJECTS_NUMBER)])
                i += 1
        logger.info('Operation executed in {} seconds'.format(datetime.now().timestamp() - start_time))
