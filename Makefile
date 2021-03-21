sqlite:
	date
	python main.py "sqlite:///data.sqlite3"
	date

build:
	docker kill pdl-sql || true
	docker rm pdl-sql || true
	docker run --name pdl-sql -p 5555:5432 -e POSTGRES_HOST_AUTH_METHOD=trust -d postgres:11-alpine
	echo "Letting postgres warm up..."
	sleep 5
	docker exec pdl-sql psql -U postgres -c "DROP DATABASE airline" || true
	docker exec pdl-sql psql -U postgres -c "CREATE DATABASE airline"
	date
	python main.py -vv --weeks 1 "postgresql://postgres@localhost:5555/airline"
	date

push:
	docker exec -it pdl-sql /bin/mkdir -p /pdl
	docker exec -it pdl-sql /bin/cp -R /var/lib/postgresql/data /pdl
	docker commit $$(docker ps | grep pdl-sql | cut -d " " -f 1) logstoneducation/pdl-advanced-sql:latest
	docker push logstoneducation/pdl-advanced-sql:latest

dump:
	pg_dump -U postgres -h 127.0.0.1 -p 5555 -d airline --no-owner --no-comments > airline.sql

gzip: dump
	gzip airline.sql
	echo "Upload airline.sql.gz to GCS"

clean:
	rm data.sqlite3 build.log || true
	docker kill pdl-sql || true
	docker rm pdl-sql || true
