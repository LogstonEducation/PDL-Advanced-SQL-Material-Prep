export DBPORT=5555
docker kill pdl-sql
docker rm pdl-sql
docker run --name pdl-sql -p $DBPORT:5432 -d postgres:latest
sleep 5

docker exec pdl-sql psql -U postgres -c "DROP DATABASE airline"
docker exec pdl-sql psql -U postgres -c "CREATE DATABASE airline"

date
pipenv run python main.py "postgresql://postgres@localhost:$DBPORT/airline"
date

