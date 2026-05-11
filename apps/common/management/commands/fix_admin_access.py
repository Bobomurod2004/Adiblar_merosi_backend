from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


User = get_user_model()


class Command(BaseCommand):
    help = "Barcha superadminlar uchun staff/active/superuser flaglarini to'g'rilaydi."

    def handle(self, *args, **options):
        updated_count = 0

        for user in User.objects.filter(is_superuser=True):
            changed = False

            if not user.is_staff:
                user.is_staff = True
                changed = True
            if not user.is_active:
                user.is_active = True
                changed = True

            if changed:
                user.save(update_fields=['is_staff', 'is_active'])
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Tuzatilgan superadminlar soni: {updated_count}"))
        self.stdout.write(self.style.SUCCESS("Superadmin kirish huquqlari tekshirildi."))
