from random import randint

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils.datetime_safe import datetime
from faker import Faker

from forum.management.commands.logger import make_logger
from forum.management.commands.random_getter import get_random
from forum.models import Like

fake = Faker()

fake.name()


class Command(BaseCommand):
    DEBUG_MODE = False

    def add_arguments(self, parser):
        parser.add_argument('likes', type=int)

        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode',
        )

    def handle(self, *args, **options):
        logger = make_logger(options['debug'])
        start_time = datetime.now().timestamp()
        logger.info('Generating {} likes...'.format(options['likes']))
        total_likes = options['likes']
        i = 0
        while i < total_likes:
            user = get_random(User)
            for j in range(randint(5, 40)):
                logger.info('Generate {} / {} like.'.format(i + 1, options['likes']))
                like = Like(user=user, is_active=False)
                like.save()
                i += 1
        logger.info('Operation executed in {} seconds'.format(datetime.now().timestamp() - start_time))
