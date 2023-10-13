#  Foodgram

[![Main foodgram workflow](https://github.com/zalgan05/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/zalgan05/foodgram-project-react/actions/workflows/main.yml)

Проект позволяет публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта  доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Настроить запуск проекта Foodgram в контейнерах

Заполнить файл .env. Пример в файле .env.example

Скопировать файл docker-compose.production.yml и запустить командой:
```python
docker compose -f docker-compose.production.yml up -d
```

### Возможности workflow

* Сборка и публикация образов бекэнда, фронтэнда, nginx на DockerHub.
* Автоматический деплой на удаленный сервер.
* Отправка уведомления в телеграм-чат.

Для корректной работы необходимо добавить в Secrets GitHub:
* DOCKER_USERNAME - ник в Docker
* DOCKER_PASSWORD - пароль в Docker
* HOST - IP-адрес вашего сервера
* USER - ваше имя пользователя
* SSH_KEY - закрытый SSH-ключ
* SSH_PASSPHRASE - ваш passphrase
* TELEGRAM_TO - ID вашего телеграм-аккаунта
* TELEGRAM_TOKEN - токен вашего телеграм бота

## Технологии

* Python 3.9
* Django 3.2
* Django REST framework 3.14
* Nginx
* Docker
* Postgres
* GitHub Actions

## Примеры запросов

<details>
<summary>Главная страница</summary>

![главный](https://github.com/zalgan05/foodgram-project-react/assets/119598678/0f0f5ea0-72f4-4324-b309-84923a306835)

</details>

<details>
<summary>Рецепт</summary>

![рецепт](https://github.com/zalgan05/foodgram-project-react/assets/119598678/cf0a5f70-f4a0-4c55-9be5-f266edb2e230)

</details>

<details>
<summary>Список покупок</summary>

![список покупок](https://github.com/zalgan05/foodgram-project-react/assets/119598678/eb9c851c-28b7-4c94-9048-bb43e42e5265)

</details>

## Backend by

[zalgan05](https://github.com/zalgan05)
