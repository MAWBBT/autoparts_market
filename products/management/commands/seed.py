from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product

User = get_user_model()


class Command(BaseCommand):
    help = 'Создание тестовых данных для магазина АвтоДеталь'

    def handle(self, *args, **options):
        # Демо-пользователь для входа (логин = email)
        demo_email = 'admin@autodetail.ru'
        demo_password = 'admin'
        user, created = User.objects.get_or_create(
            username=demo_email,
            defaults={'email': demo_email, 'is_staff': True, 'is_superuser': True},
        )
        if created:
            user.set_password(demo_password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Создан демо-пользователь: {demo_email} / {demo_password}'))
        else:
            user.set_password(demo_password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Пароль демо-пользователя обновлён: {demo_email} / {demo_password}'))

        try:
            from main.models import UserProfile
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'full_name': 'Администратор', 'phone': '+7 (495) 123-45-67'},
            )
        except Exception:
            pass

        categories_data = [
            {'name': 'Тормозная система', 'slug': 'brakes', 'description': 'Тормозные колодки, диски, суппорты'},
            {'name': 'Масла и жидкости', 'slug': 'oils', 'description': 'Моторные масла, жидкости'},
            {'name': 'Фильтры', 'slug': 'filters', 'description': 'Воздушные, масляные, салонные фильтры'},
            {'name': 'Электрооборудование', 'slug': 'electrical', 'description': 'Свечи, аккумуляторы'},
            {'name': 'Ремни и приводы', 'slug': 'belts', 'description': 'Ремни ГРМ, приводные ремни'},
        ]
        for cat_data in categories_data:
            Category.objects.get_or_create(slug=cat_data['slug'], defaults=cat_data)

        products_data = [
            {
                'category_slug': 'brakes',
                'article': 'BRK-001',
                'name': 'Тормозные колодки передние',
                'slug': 'tormoznye-kolodki-perednie',
                'description': 'Оригинальные тормозные колодки для большинства японских автомобилей. Высокое качество, низкий уровень шума, долгий срок службы.',
                'price': 2500,
                'stock': 30,
            },
            {
                'category_slug': 'oils',
                'article': 'OIL-005',
                'name': 'Моторное масло 5W-40',
                'slug': 'motornoe-maslo-5w40',
                'description': 'Синтетическое моторное масло премиум класса. Подходит для бензиновых и дизельных двигателей. 4 литра.',
                'price': 1800,
                'stock': 50,
            },
            {
                'category_slug': 'filters',
                'article': 'FLT-012',
                'name': 'Воздушный фильтр',
                'slug': 'vozdushnyj-filtr',
                'description': 'Универсальный воздушный фильтр для иномарок. Обеспечивает максимальную пропускную способность и защиту двигателя.',
                'price': 850,
                'stock': 0,
                'delivery_days': '3 дня',
            },
            {
                'category_slug': 'electrical',
                'article': 'SPK-018',
                'name': 'Свечи зажигания (комплект 4 шт)',
                'slug': 'svechi-zazhiganiya-komplekt',
                'description': 'Иридиевые свечи зажигания. Увеличенный ресурс работы, стабильное искрообразование, экономия топлива.',
                'price': 3200,
                'stock': 25,
            },
            {
                'category_slug': 'electrical',
                'article': 'BAT-022',
                'name': 'Аккумулятор 60Ah',
                'slug': 'akkumulyator-60ah',
                'description': 'Необслуживаемый аккумулятор повышенной ёмкости. Пусковой ток 540А. Гарантия 2 года.',
                'price': 5500,
                'stock': 15,
            },
            {
                'category_slug': 'belts',
                'article': 'BLT-007',
                'name': 'Ремень ГРМ',
                'slug': 'remen-grm',
                'description': 'Качественный ремень газораспределительного механизма.',
                'price': 1200,
                'stock': 20,
            },
        ]
        for prod in products_data:
            cat = Category.objects.get(slug=prod.pop('category_slug'))
            Product.objects.get_or_create(
                slug=prod['slug'],
                defaults={
                    **prod,
                    'category': cat,
                }
            )
        self.stdout.write(self.style.SUCCESS('Тестовые данные созданы!'))
