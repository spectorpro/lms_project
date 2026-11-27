from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создаёт группу модераторов"

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="moderators")
        if created:
            self.stdout.write(self.style.SUCCESS("Группа moderators создана"))
        else:
            self.stdout.write("Группа moderators уже существует")
