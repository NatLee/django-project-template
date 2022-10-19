# Backend Template

## Requirements

Please specify the required variables in `.env` for this project.

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

- [Admin](http://localhost/api/__hidden_admin)

- [Redoc](http://localhost/api/__hidden_redoc)

- [Swagger](http://localhost/api/__hidden_swagger)

- [Session Login with Rest Framework](http://localhost/api/__hidden_dev_dashboard/login)

- [JWT Login](http://localhost/api/__hidden_dev_dashboard/login)

- [User dashboard](http://localhost/api/__hidden_dev_dashboard/dashboard)
