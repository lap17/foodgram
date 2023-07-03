# Проект Foodgram
![example workflow](https://github.com/lusha17/foodgram-project-react/workflows/foodgram_workflow.yml/badge.svg)  

Foodgram реализован для публикации рецептов. Авторизованные пользователи
могут подписываться на понравившихся авторов, добавлять рецепты в избранное,
в покупки, скачать список покупок ингредиентов для добавленных в покупки
рецептов.

## Подготовка и запуск проекта

* Склонируйте репозиторий на локальную машину:
    ```
    git clone https://github.com/lusha17/foodgram-project-react
    ```
* Выполните вход на свой удаленный сервер (ubuntu).

* Установите docker на сервер:
    ```
    sudo apt install docker.io 
    ```
* Установите docker-compose на сервер:
    ```
    sudo apt install docker-compose
    ```
* Локально отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP.
* Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на сервер:
    ```
    scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
    scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
    ```
* Cоздайте .env файл и впишите:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<название базы данных postgres>
    POSTGRES_USER=<пользователь бд>
    POSTGRES_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    SECRET_KEY=<секретный ключ проекта django>
    ```
* Для работы с Workflow добавьте в Secrets GitHub переменные окружения для работы:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<название базы данных postgres>
    POSTGRES_USER=<пользователь бд>
    POSTGRES_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    
    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя>
    
    SECRET_KEY=<секретный ключ проекта django>
    ALLOWED_HOSTS=<список разрешенных хостов для проекта django через запятую>

    USER=<username для подключения к серверу>
    HOST=<IP сервера>
    SSH_KEY=<ваш SSH ключ (для получения используйте команду со своего компьютера: cat ~/.ssh/id_rsa)>

    TELEGRAM_TO=<ID чата, в который придет сообщение>
    TELEGRAM_TOKEN=<токен вашего бота>
    ```
    Workflow состоит из трёх шагов:
     - Проверка кода на соответствие PEP8
     - Сборка и публикация образа бекенда на DockerHub.
     - Автоматический деплой на удаленный сервер.
     - Отправка уведомления в телеграм-чат.  

* После успешной сборки на сервере выполните команды (только после первого деплоя):
    - Соберите статические файлы:
    ```
    sudo docker-compose exec backend python manage.py collectstatiс
    ```
    - Примените миграции:
    ```
    sudo docker-compose exec backend python manage.py makemigrations
    ```
    ```
    sudo docker-compose exec backend python manage.py migrate
    ```
    - Загрузите ингредиенты и теги в базу данных:
    ```
    sudo docker-compose exec backend python manage.py load 
    ```
    - Создайте суперпользователя Django:
    ```
    sudo docker-compose exec backend python manage.py createsuperuser 
    ```
    - Проект будет доступен по вашему IP