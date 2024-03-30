# Проект "Фудграм"

[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)

## Описание проекта "Фудграм"

Проект «Фудграм» — сайт, на котором пользователи публикуют рецепты, 
добавляют чужие рецепты в избранное и подписываются на публикации других 
авторов. Пользователям сайта также доступен сервис «Список покупок». 
Он позволяет создавать список продуктов, которые нужно купить для 
приготовления выбранных блюд.  

## Уровни доступа пользователей:  

### Возможности неавторизованных пользователей:
- Просмотр рецептов на главной странице
- Просмотр отдельных страниц рецептов
- Просмотр страниц пользователей
- Создание аккаунта

### Возможности авторизованных пользователей:
- Вход в систему под своим логином и паролем
- Выход из системы
- Создание, редактирование и удаление собственных рецептов
- Просмотр страниц пользователей
- Просмотр отдельных страниц рецептов
- Просмотр рецептов на главной странице
- Фильтрация рецептов по тегам
- Работа с персональным списком покупок: добавление и удаление любых рецептов, выгрузка файла с количеством необходимых ингредиентов для рецептов из списка покупок
- Работа с персональным списком избранного: добавление в него рецептов или удаление их, просмотр своей страницы избранных рецептов
- Подписка на публикации авторов рецептов и отмена подписки, просмотр своей страницы подписок

### Возможности администратора:
- Все права авторизованного пользователя
- Изменение пароля любого пользователя
- Создание, блокировка и удаление аккаунтов пользователей
- Редактирование и удаление любых рецептов
- Добавление, удаление и редактирование ингредиентов
- Добавление, удаление и редактирование тегов

## Запуск проекта локально

- Клонируйте репозиторий и перейдите в него в командной строке:
```
git clone git@github.com:cskovec22/foodgram-project-react.git
cd foodgram-project-react
```

- Установите и активируйте виртуальное окружение:

```
python -m venv venv
```

- Для Linux/macOS:

    ```
    source venv/bin/activate
    ```

* Для Windows:

    ```
    source venv/Scripts/activate
    ```

Установите зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- Создайте файл .env в папке проекта, пример представлен в файле ./infra/.env.example  


- Перейдите в папку с файлом manage.py


- Примените миграции:
```
python manage.py makemigrations
python manage.py migrate
```

- Соберите статику:
```
python manage.py collectstatic
```

- Создайте суперпользователя:
```
python manage.py createsuperuser
```

- Заполните базу данных командой:
```
python manage.py importcsv
```

- Запустите проект:
```
python manage.py runserver
```

- Документацию можно посмотреть по адресу:
```
http://127.0.0.1:8000/api/docs/
```

## Запуск проекта в контейнерах:

- Установите docker и docker-compose


- Создайте директорию foodgram/infra


- Создайте в этой директории файл .env, пример представлен в файле ./infra/.env.example  


- Скопируйте файл проекта docker-compose.production.yml в директорию foodgram/infra и разверните контейнеры командой:
```
sudo docker compose -f docker-compose.production.yml up -d --build
```

- Выполните миграции:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

- Заполните базу данных командой:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py importcsv
```

- Соберите статику:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

- Создайте суперпользователя:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```


- Для остановки проекта выполните команду:
```
sudo docker compose -f docker-compose.production.yml down
```

## Список эндпоинтов API:

- /api/users/ - список пользователей и их регистрация
- /api/users/{id}/ - профиль пользователя
- /api/users/me/ - текущий пользователь
- /api/users/set_password/ - изменение пароля текущего пользователя
- /api/auth/token/login/ - получить токен авторизации
- /api/auth/token/logout/ - удалить токен текущего пользователя
- /api/tags/ - список тегов
- /api/tags/{id}/ - получение тега
- /api/recipes/ - получение списка рецептов или создание нового
- /api/recipes/{id}/ - получение, обновление или удаление рецепта
- /api/recipes/download_shopping_cart/ - скачать список покупок
- /api/recipes/{id}/shopping_cart/ - добавить или удалить рецепт из списка покупок
- /api/recipes/{id}/favorite/ - добавить или удалить рецепт из избранного
- /api/users/subscriptions/ - возвращает пользователей, на которых подписан текущий пользователь
- /api/users/{id}/subscribe/ - подписаться или отписаться от пользователя
- /api/ingredients/ - список ингредиентов
- /api/ingredients/{id}/ - получение ингредиента

Подробную информацию по эндпоинтам API можно посмотреть по адресу:
```
http://localhost/api/docs/
```

### Автор:  
*Васин Никита*  
**email:** *cskovec22@yandex.ru*  
**telegram:** *@cskovec22*  
**VK:** https://vk.com/cskovec22