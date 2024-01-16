#!/bin/sh

# Wait 60 seconds for SQL Server to start up by ensuring that
# calling SQLCMD does not return an error code, which will ensure that sqlcmd is accessible
# and that system and user databases return "0" which means all databases are in an "online" state
# https://docs.microsoft.com/en-us/sql/relational-databases/system-catalog-views/sys-databases-transact-sql?view=sql-server-2017
echo "Waiting for SQL Server..."
DBSTATUS=1
ERRCODE=1
i=0

while [ $DBSTATUS -ne 0 ] && [ $i -lt 60 ] && [ $ERRCODE -ne 0 ]; do
  i=$i+1
  DBSTATUS=$(/opt/mssql-tools/bin/sqlcmd -h -1 -t 1 -U sa -P $MSSQL_SA_PASSWORD -Q "SET NOCOUNT ON; Select SUM(state) from sys.databases")
  ERRCODE=$?
  sleep 1
done

echo "SQL Server started"

echo "Waiting for default db..."

#waiting for postgres
until psql --host=$DB_HOST --username=$DB_USER $DB_NAME -w &>/dev/null
do
  echo "Waiting for PostgreSQL..."
  sleep 1
done

echo "Postgres is ready, running the migrations..."

alembic upgrade head
uvicorn main:app --reload --host 0.0.0.0 --port 8000