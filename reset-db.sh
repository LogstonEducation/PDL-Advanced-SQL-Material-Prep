
docker kill pdl-sql
docker rm pdl-sql
docker run --name pdl-sql -p 5555:5432 -d postgres:latest
