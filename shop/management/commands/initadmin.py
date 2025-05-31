from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from account.models import User  # تغییر به مدل User سفارشی

class Command(BaseCommand):
    help = 'Creates a superuser if none exists'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the superuser')
        parser.add_argument('email', type=str, help='Email for the superuser')
        parser.add_argument('password', type=str, help='Password for the superuser')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully'))
            else:
                self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists'))
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}')) 