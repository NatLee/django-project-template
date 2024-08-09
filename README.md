# Django Backend Template

![cover][./doc/cover.png]

This is a Django backend template. It includes some useful features and tools.

## Requirements

Please specify the required variables in `.env` for this project.

## Features

- Docker
- Backend -> Django 5
- Database -> MariaDB
- Load Balancer -> NGINX

## Other Features

- API Proxy -> api_proxy
- User login history -> django_login_history
- Login Playground (Session, JWT) -> dev_dashboard
- 3rd Party Login with JWT -> Custom Allauth Adapter (authentication)
- Websocket(WSGI) -> Django Channels
- Async Task -> Django Q2
- Admin Page -> Django Unfold
- Documentation -> Redoc, Swagger

## Usage

### Quick Start

```bash
docker-compose build && docker-compose up
```

### Rebuild

Clean up and rebuild.

```bash
rm -rf backend-sql-data &&  docker-compose down -v && docker-compose build && docker-compose up
```

### 3rd Party Login

You can check the setting in [here](https://github.com/NatLee/Django-Simple-3rd-Party-JWT?tab=readme-ov-file#backend).

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

## Playground

The playground is a place to test the login system and websocket.

- DEV dashboard: http://localhost:5566/api/__hidden_dev_dashboard

- Websocket Test Page: http://localhost:5566/api/ping/index

## Link

> Here's port `5566` is an example. You can define it in `.env` file.

- Admin: http://localhost:5566/api/__hidden_admin/

- Redoc: http://localhost:5566/api/__hidden_redoc

- Swagger: http://localhost:5566/api/__hidden_swagger
