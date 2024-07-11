# Django Backend Template

This is a template that can be used creating a Django project.

## Requirements

Please specify the required variables in `.env` for this project.

## Features

- Backend -> Django
- Database -> MariaDB
- Load Balancer -> NGINX

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

## Tools

- DEV dashboard: http://localhost:5566/api/__hidden_dev_dashboard

- Websocket Test Page: http://localhost:5566/api/ping/index


## Link

> Here's port `5566` is an example. You can define it in `.env` file.

- Admin: http://localhost:5566/api/__hidden_admin/

- Redoc: http://localhost:5566/api/__hidden_redoc

- Swagger: http://localhost:5566/api/__hidden_swagger

- Session Login with Rest Framework: http://localhost:5566/api/__hidden_dev_dashboard/login

- JWT Login: http://localhost:5566/api/__hidden_dev_dashboard/login
