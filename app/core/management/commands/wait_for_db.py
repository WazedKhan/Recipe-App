"""
Django command to wait for db to be avilable.
"""
import time
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as Psycopg2OpError


class Command(BaseCommand):
    """command class to wait for database"""

    def handle(self, *args, **options):
        """Entrypoint for command"""
        self.stdout.write('Waiting for database.........')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavilable, \
                                  waiting 1 sec ........')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database Available.'))
