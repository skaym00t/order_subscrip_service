Сборка проекта:
```bash
docker-compose build 
```
Запуск проекта:
```bash
docker-compose up
```
Остановка проекта:
```bash
docker-compose stop
```
Создание и применение миграций:
```bash
docker-compose run --rm service-app sh -c "python manage.py migrate"
```
Создание суперпользователя:
```bash
docker-compose run --rm app python manage.py createsuperuser
```
