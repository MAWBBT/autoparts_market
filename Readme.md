# Интернет-магазин автозапчастей

Веб-приложение интернет-магазина автозапчастей, разработанное на Django с использованием PostgreSQL в качестве системы управления базами данных.

## Функциональные возможности

### Основные страницы
- **Главная страница** - общая информация о магазине, акции, новинки
- **Каталог товаров** - просмотр всех доступных автозапчастей
- **Корзина** - управление выбранными товарами с расчетом итоговой стоимости
- **Вход/Регистрация** - система аутентификации пользователей

### Безопасность
- Хэширование паролей пользователей с использованием современных алгоритмов
- Защищенные сессии пользователей
- Безопасное хранение учетных данных

### Каталог товаров
Каждая деталь в каталоге содержит:
- **Идентификатор детали** - уникальный артикул товара
- **Изображение детали** - визуальное представление товара
- **Наименование** - название автозапчасти
- **Описание** - подробные характеристики и особенности
- **Наличие** - статус наличия на складе
- **Срок доставки** - время доставки при отсутствии на складе
- **Цена** - стоимость товара

### Поисковая система
Возможность поиска деталей по:
- Наименованию товара
- Идентификатору (артикулу)
- Описанию товара

### Корзина покупок
- Отображение всех добавленных товаров
- Возможность изменения количества
- Удаление товаров из корзины
- Расчет итоговой суммы с учетом:
  - Стоимости всех товаров
  - Стоимости доставки

## Технологический стек

### Backend
- **Django** - основной фреймворк
- **Django ORM** - работа с базой данных
- **Django Authentication** - система аутентификации

### База данных
- **PostgreSQL** - реляционная СУБД для хранения данных

### Frontend
- **HTML5** - разметка страниц
- **CSS3** - стилизация
- **JavaScript** - интерактивные элементы
- **Bootstrap** (опционально) - для адаптивного дизайна

## Структура проекта

```
autoparts_store/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── .env
├── .gitignore
└── autoparts/
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    └── asgi.py
└── apps/
    ├── users/           # Приложение пользователей
    ├── catalog/         # Приложение каталога
    ├── cart/           # Приложение корзины
    └── orders/         # Приложение заказов
```

## Установка и запуск

### Предварительные требования
- Python 3.8+
- PostgreSQL 12+
- pip (менеджер пакетов Python)

### Шаги установки

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd autoparts-store
```

2. **Создание виртуального окружения**
```bash
python -m venv venv
source venv/bin/activate  # Для Linux/Mac
# или
venv\Scripts\activate     # Для Windows
```

3. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

4. **Настройка базы данных PostgreSQL**
```sql
CREATE DATABASE autoparts_db;
CREATE USER autoparts_user WITH PASSWORD 'your_password';
ALTER ROLE autoparts_user SET client_encoding TO 'utf8';
ALTER ROLE autoparts_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE autoparts_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE autoparts_db TO autoparts_user;
```

5. **Настройка переменных окружения**
Создайте файл `.env` в корневой директории:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=autoparts_db
DB_USER=autoparts_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

6. **Настройка Django**
В `autoparts/settings.py` убедитесь в правильности конфигурации:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

7. **Применение миграций**
```bash
python manage.py makemigrations
python manage.py migrate
```

8. **Создание суперпользователя**
```bash
python manage.py createsuperuser
```

9. **Запуск сервера разработки**
```bash
python manage.py runserver
```

10. **Доступ к приложению**
Откройте браузер и перейдите по адресу:
```
http://127.0.0.1:8000/
```

Панель администратора доступна по адресу:
```
http://127.0.0.1:8000/admin/
```

## Модели данных

### Основные модели:
- **User** - пользователи системы
- **Product** - товары (автозапчасти)
- **Category** - категории товаров
- **Cart** - корзина пользователя
- **CartItem** - элементы корзины
- **Order** - заказы
- **OrderItem** - элементы заказа

## Административная панель

Панель администратора Django предоставляет возможности:
- Управление товарами (добавление, редактирование, удаление)
- Управление категориями
- Просмотр и управление заказами
- Управление пользователями

## Тестирование

Для запуска тестов выполните:
```bash
python manage.py test
```

## Развертывание

### Для production среды:
1. Установите `DEBUG=False` в настройках
2. Настройте статические файлы:
```bash
python manage.py collectstatic
```
3. Используйте production-сервер (Gunicorn + Nginx)
4. Настройте SSL-сертификат для HTTPS

## Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Запушьте ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request