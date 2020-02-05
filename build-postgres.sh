docker kill pdl-sql
docker rm pdl-sql
docker run --name pdl-sql -p 5555:5432 -d postgres:latest
sleep 5
date
python main.py "postgresql://postgres@localhost:5555"
date
