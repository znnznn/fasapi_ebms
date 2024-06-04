# Wiseline FastApi

## General URL’s

| **Provider**                    | **Service Name** | **URL** |
|:--------------------------------|:-----------------|:--------|
| Hosting provider                | AWS              | -       |
| CI/CD provider                  | github actionc   |         |
| Logs provider                   | AWS              | -       |

## Tech details

|               **Resource**                | **Resource Name** | **Version** | **Comment**  |
|:-----------------------------------------:|:-----------------:|:-----------:|:------------:|
|       Back-end programming language       |      python       |    3.11     |              |
|          Back-end web framework           |      FastApi      |             |              |
|             Default Database              |     Postgres      |             |     AWS      |
|               EBMS Database               |   MS SQL Server   |             |    Azure     |
|                Web server                 |      uvicorn      |             |   gunicorn   |
|                   REDIS                   |       REDIS       |             |              |
|            Front-end language             |       React       |    Vite     | + TypeScript |

## Application URL’s

| **Environment** | **Service Name** | **URL**                          |
|:----------------|:-----------------|:---------------------------------|
| Production      | Website          | <https://dev-ebms.fun/>          |
|                 | Swagger          | <https://api.dev-ebms.fun/docs/> |

## Installation & Launch

## Run command with docker

Run project with docker.
You need install docker
need set environments

```commandline
docker-compose up --build
```

# After docker run app has 5 containers:

- BACKEND
- REDIS
- DB

## Run commands

Needs add environments vars

|             **PARTH**             |                      **Commands**                       |           **Description**           |
|:---------------------------------:|:-------------------------------------------------------:|:-----------------------------------:|
|           Requirements            |                   pip install pipenv                    |                                     |
|           Requirements            |                     pipenv install                      | this installed dependencies to venv |
|        Start django server        | uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 |      <http://127.0.0.1:8000/>       |
|            Stop server            |                        ctrl + C                         |                                     |
| Run migrations or database schema |                  alembic upgrade head                   |                                     |

## Dev environment deployment

Populate `Environment variables` of your system with the following:

```bash
export DEBUG # default False
export SECRET_KEY

# settings for default database
export DB_NAME
export DB_USER
export DB_PASS
export DB_HOST=db
export DB_PORT=5432

# settings for EBMS Database
export EBMS_DB_NAME
export EBMS_DB_USER
export EBMS_DB_HOST
export MSSQL_SA_PASSWORD
export EBMS_DB_PORT=1433

# for login
export ACCESS_TOKEN_EXPIRE_MINUTES

export ACCEPT_EULA

#for sending emails
export RESEND_FROM_EMAIL
export RESEND_API_KEY

# for create super admin
export TOKEN_CREDENTIAL

# for connection to EBMS Rest API
export EBMS_API_URL
export EBMS_API_LOGIN
export EBMS_API_PASSWORD

# for websockets
export REDIS_HOST
export REDIS_URL

```

Then install all the required packages:

# BACKEND

```bash
user@host$ cd wiseline-fastapi/
```

```bash
user@host$ pip install pipenv
user@host$ pipenv install
user@host$ gunicorn main:app -w 2 --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornH11Worker
```

# FRONTEND

```bash
user@host$ npm install
user@host$ npm run dev
```
