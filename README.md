# Backend Template

## Requirements

Please specify the required variables for this project.

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

## Usage

```bash
docker-compose build && docker-compose up
```

Clean up and rebuild.

```bash
rm -rf backend-sql-data &&  docker-compose down -v && docker-compose build && docker-compose up
```

## Check

- Admin
  http://localhost/\_\_hiddenadmin/

- Swagger
  http://localhost/\_\_hiddenswagger/

- Redoc
  http://localhost/redoc/

- Rest Framework
  http://localhost/accounts/login/
