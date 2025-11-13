"""
Django management command to initialize raw SQL authentication tables
Usage: python manage.py init_raw_sql_auth
"""
from django.core.management.base import BaseCommand
from users.raw_sql_auth.db_schema import init_auth_tables


class Command(BaseCommand):
    help = 'Initialize authentication tables for raw SQL authentication'

    def handle(self, *args, **options):
        self.stdout.write('Initializing raw SQL authentication tables...')

        try:
            init_auth_tables()
            self.stdout.write(
                self.style.SUCCESS('Successfully initialized authentication tables')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to initialize tables: {str(e)}')
            )
