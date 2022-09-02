# Backend Template

## Requirements

Please specify the required variables in `.env` for this project.

```
DEBUG=True
MARIADB_ALLOW_EMPTY_ROOT_PASSWORD=True
MYSQL_ROOT_PASSWORD=""
MYSQL_DATABASE=testdb
MYSQL_USER=testuser
MYSQL_PASSWORD=testpassword
DATABASE_PORT=3306
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=1234
DJANGO_SUPERUSER_EMAIL=admin@admin.com
```

If `DEBUG` is True, it'll use SQLite as database.

## Usage

```bash
docker-compose build && docker-compose up
```

Clean up and rebuild.

- Debug

```bash
rm ./backend/db.sqlite3 &&  docker-compose down -v && docker-compose build && docker-compose up
```

- Production

```bash
rm -rf backend-sql-data &&  docker-compose down -v && docker-compose build && docker-compose up
```

## Link

- [Admin](http://localhost/__hiddenadmin/)

- [Redoc](http://localhost/redoc/)

- [Swagger](http://localhost/__hiddenswagger)

- [Session Login with Rest Framework](http://localhost/accounts/login/)

- [JWT Login](http://localhost/__user/login)

- [User dashboard](http://localhost/__user/dashboard)
