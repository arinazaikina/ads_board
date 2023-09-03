# Учебный проект доска объявлений ADS ONLINE

## Запуск проекта

На машине, где разворачивается проект, должны быть установлены docker и docker-compose.
Для их установки обратитесь к официальной документации.

1. Открыть терминал
2. С помощью команды `cd` перейти в каталог, где будет размещен проект
3. Выполнить команду для клонирования проекта

```bash
git clone https://github.com/arinazaikina/ads_board.git
```

4. Перейти в каталог проекта

```bash
cd ads_board
```

5. В корневой папке проекта создать файл `.env`

```bash
touch .env
```

6. Открыть файл

```bash
nano .env
```

7. Записать в файл следующие настройки

```
POSTGRES_USER=
POSTGRES_DB=
POSTGRES_PORT=5432
POSTGRES_PASSWORD=
POSTGRES_HOST=db_ads

EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

HOST=127.0.0.1
CORS_ORIGIN=http://127.0.0.1:3000
```

Не менять значения `POSTGRES_HOST=db_habit`.
Для локального запуска `HOST` и `CORS_ORIGIN` также можно не менять.
Для запуска на удаленном сервере `127.0.0.1` надо заменить на публичный IP-адрес.

В каталоге проекта есть шаблон `.env.template`

8. Запустить проект с помощью Docker, используя следующую команду:

```bash
docker-compose build --no-cache && docker-compose up -d
```

9. Дождаться, когда контейнер с именем `frontend_ad` будет иметь статус `Exited (0)`, а другие
   контейнеры (`nginx_ads`, `backend_ads`, `db_ads`) -
   статус `Up`.


10. Выполнить миграции и загрузить тестовые данные

```bash
docker exec -t backend_ads bash
```

```bash
python manage.py migrate
```

```bash
python manage.py loaddata data.json
```

```bash
exit
```

## Доступ к сервису

Показаны ссылки для случая запуска на локальной машине.
Если запуск был на удаленном сервере, то 127.0.0.1 необходимо заменить на публичный IP-адрес.

* Сайт: http://127.0.0.1:3000
* Swagger: http://127.0.0.1:8000/swagger/
* Взаимодействие с API по следующему URL: http://127.0.0.1:8000/api/
* Административная панель: http://127.0.0.1:8000/api/admin

## Описание проекта

После загрузки тестовых данных, что было сделано на шаге 10, будут доступны 3 пользователя.

* Супер пользователь: admin@mail.com, пароль 0000.
* Пользователь sav2405@gmail.com с ролью `admin`, пароль qwerty123!
* Пользователь max@mail.com с ролью `user`, пароль qwerty123!

Проект представляет собой backend-часть для доски объявлений.

Реализован следующий функционал:

* авторизация и аутентификация пользователей;
* распределение ролей между пользователями (пользователь и админ);
* восстановление пароля через электронную почту.
* CRUD для объявлений и отзывов на сайте;
* поиск объявлений по названию.

### Права доступа

**Анонимный пользователь может**:

- получать список объявлений.

**Пользователь может:**

- получать список объявлений,
- получать одно объявление,
- создавать объявление,
- редактировать и удалять свое объявление,
- получать список комментариев,
- создавать комментарии,
- редактировать/удалять свои комментарии;
- редактировать свой профиль;
- восстанавливать пароль.

**Администратор может:**

- дополнительно к правам пользователя редактировать или удалять
  объявления и комментарии любых других пользователей через административную панель.

Супер пользователь через административную панель может выдать другим пользователем роль `admin`, после чего
они будут иметь право удалять и редактировать любые объявления и отзывы через административную панель.
Чтобы пользователь имел доступ к административной панели, супер пользователь должен установить пользователю не только
роль `admin`, а также установить ему статус персонала (`is_staff`).

### Регистрация и авторизация

Пользователи могут зарегистрироваться в системе и войти в свою учетную запись,
чтобы получить доступ к персонализированным функциям.

Авторизация в API происходит с помощью механизма токенов.
Чтобы получить токен, необходимо передать свои учетные данные (электронную почту и пароль)
на конечную точку /token. В ответе будет отправлен токен доступа.

Для доступа к защищенным конечным точкам API, этот токен должен быть включен в заголовки
всех последующих HTTP-запросов.
Необходимо добавить его в заголовок Authorization следующим образом:
Authorization: Bearer ваш_токен, где ваш_токен - это токен, который был получен при входе в систему.

### Объявления

Неавторизованный пользователь может просматривать только список объявлений, без просмотра детальной информации.
Авторизованный пользователь может просматривать список объявлений, детальную информацию по объявлению,
создавать объявления, удалять и редактировать свои объявления.

### Отзывы

Неавторизованный пользователь не видит отзывы.
Авторизованный пользователь может просматривать все отзывы, редактировать и удалять свои отзывы.

### Профиль

Авторизованный пользователь может менять данные профиля (имя, фамилию, телефон, аватарку)

### Пагинация

Для удобства просмотра списка объявлений реализована пагинация, которая выводит по 4 объявления на страницу.

### Безопасность

Настроен CORS для развернутого сервера, что позволяет фронтенду подключаться к проекту безопасно.

### Документация

Документация приложения содержит описание эндпоинтов и их работы,
что поможет разработчикам фронтенда легко использовать функционал приложения.

## Используемые технологии

В разработке проекта использовались следующие технологии:

* Python: основной язык программирования проекта.
* Django Rest Framework (DRF): основной фреймворк для разработки API.
* PostgreSQL: система управления базами данных, которая используется для хранения и обработки данных.
* Docker: используется для контейнеризации приложения
* flake8, black, isort для статического анализа кода