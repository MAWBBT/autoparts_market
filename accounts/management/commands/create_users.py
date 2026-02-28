from django.core.management.base import BaseCommand
from accounts.models import User, UserRole


class Command(BaseCommand):
    help = 'Создание тестового пользователя и администратора в базе данных'

    def handle(self, *args, **options):
        # Создание обычного пользователя
        user_email = 'user@example.com'
        user_password = '12345678'
        user, created = User.objects.get_or_create(
            email=user_email,
            defaults={
                'full_name': 'Тестовый Пользователь',
                'role': UserRole.USER,
                'is_active': True,  # Активируем для возможности входа
            }
        )
        if created:
            user.set_password(user_password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'[OK] Создан пользователь: {user_email} / {user_password}'
                )
            )
        else:
            user.set_password(user_password)
            user.is_active = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'[OK] Пароль пользователя обновлён: {user_email} / {user_password}'
                )
            )

        # Создание администратора
        admin_email = 'admin@example.com'
        admin_password = 'admin12345'
        admin, created = User.objects.get_or_create(
            email=admin_email,
            defaults={
                'full_name': 'Администратор',
                'role': UserRole.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,  # Активируем для возможности входа
            }
        )
        if created:
            admin.set_password(admin_password)
            admin.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'[OK] Создан администратор: {admin_email} / {admin_password}'
                )
            )
        else:
            admin.set_password(admin_password)
            admin.is_staff = True
            admin.is_superuser = True
            admin.is_active = True
            admin.role = UserRole.ADMIN
            admin.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'[OK] Пароль администратора обновлён: {admin_email} / {admin_password}'
                )
            )

        self.stdout.write(self.style.SUCCESS('\n[OK] Пользователи готовы к использованию!'))
        self.stdout.write(self.style.WARNING('\nДанные для входа:'))
        self.stdout.write(f'  Пользователь: {user_email} / {user_password}')
        self.stdout.write(f'  Администратор: {admin_email} / {admin_password}')
