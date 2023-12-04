# Django Backend Template

This is a template that can be used creating a Django project.

## Requirements

Please specify the required variables in `.env` for this project.

## Usage

### Quick Start

- Only Django backend

```bash
docker-compose build && docker-compose up
```

- Nginx support

```bash
docker-compose -f docker-compose.nginx.yml build && docker-compose -f docker-compose.nginx.yml up
```

### Rebuild

Clean up and rebuild.

- SQLite

```bash
rm ./backend/db.sqlite3 &&  docker-compose down -v && docker-compose build && docker-compose up
```

- MySQL

```bash
rm -rf backend-sql-data &&  docker-compose down -v && docker-compose build && docker-compose up
```

## Misc

- Create superuser

```bash
bash dev-create-superuser.sh
```

- Enter Shell

```bash
bash dev-shell.sh
```

- Start New APP

```bash
bash dev-startapp <YOUR_NEW_APP_NAME>
```

## Link

> Here's port `3000` is an example. You can define it in `.env` file.

- Admin: http://localhost:3000/api/__hidden_admin/

- Redoc: http://localhost:3000/api/__hidden_redoc

- Swagger: http://localhost:3000/api/__hidden_swagger

- Session Login with Rest Framework: http://localhost:3000/api/__hidden_dev_dashboard/login

- JWT Login: http://localhost:3000/api/__hidden_dev_dashboard/login

- DEV dashboard: http://localhost:3000/api/__hidden_dev_dashboard