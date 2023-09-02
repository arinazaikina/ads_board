# Учебный проект доска объявлений ADS ONLINE

## Запуск проекта

1. Открыть терминал
2. С помощью команды `cd` перейти в каталог, где будет размещен проект
3. Выполнить команду для клонирования проекта
```bash
git clone https://github.com/arinazaikina/habit_tracker_drf_postgres_celery.git
```
4. Перейти в каталог проекта
```bash
cd habit_tracker_drf_postgres_celery
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
DJANGO_SERVER_URL=http://web:8000

POSTGRES_USER=
POSTGRES_DB=habit_db
POSTGRES_PORT=5432
POSTGRES_PASSWORD=
POSTGRES_HOST=db_habit
POSTGRES_HOST_AUTH_METHOD=trust

EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

TG_BOT_TOKEN=

CELERY_BROKER_URL='redis://redis_habit:6379/0'
CELERY_RESULT_BACKEND='redis://redis_habit:6379/0'
```
Не менять значения `DJANGO_SERVER_URL=http://web:8000`, `POSTGRES_HOST=db_habit`, 
`CELERY_BROKER_URL='redis://redis_habit:6379/0'`, `CELERY_RESULT_BACKEND='redis://redis_habit:6379/0'`

В каталоге проекта есть шаблон `.env.template`

8. Запустить проект с помощью Docker, используя следующую команду:

```bash
docker-compose build --no-cache && docker-compose up
```

9. Выполнить миграции и загрузить тестовые данные

* Зайти в контейнер backend_ads
```bash
docker exec -t backend_ads bash
```
* Выполнить миграции
```bash
python manage.py migrate
```
* Загрузить тестовые данные
```bash
python manage.py loaddata data.json
```
* Выйти из контейнера 
```bash
exit
```

## Доступ к Swagger UI

Взаимодействие с API по следующему URL: http://0.0.0.0:80/swagger/

## Описание проекта
