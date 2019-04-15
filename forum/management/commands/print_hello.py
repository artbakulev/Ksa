from django.core.management.base import BaseCommand, CommandError

from forum.models import Question as Poll


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for poll_id in options['poll_id']:
            try:
                poll = Poll.objects.all()
            except Poll.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write(self.style.SUCCESS(poll))
