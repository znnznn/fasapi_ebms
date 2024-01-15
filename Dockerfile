FROM python:3.11-slim-buster
ENV PYTHONUNBUFFERED 1

WORKDIR /app

ENV ACCEPT_EULA=Y

COPY . .

EXPOSE 8000

RUN apt-get update &&  \
    apt-get upgrade -y && \
    apt-get install -y  \
        curl \
        wget \
        libpq-dev \
        gnupg \
        libffi-dev \
        lsb-release \
        gcc \
        g++ && \
    sh -c "curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -" &&\
    sh -c "curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list" &&\
    sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
    sh -c "wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -" && \
    apt-get update && \
    apt-get install -y \
        msodbcsql17 \
        mssql-tools \
        libpython3-dev \
        libgssapi-krb5-2 \
        postgresql \
        unixodbc-dev \
        unixodbc \
        libpq5 && \
    # install application requirements
    python -m pip install --upgrade pip \
    pip install pipenv && \
    PIPENV_VENV_IN_PROJECT=1 pipenv install --system
