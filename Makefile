sqlite:
	date
	python main.py "sqlite:///data.sqlite3"
	date

docker:
	docker kill pdl-sql || true
	docker rm pdl-sql || true
	docker run --name pdl-sql -p 5555:5432 -e POSTGRES_HOST_AUTH_METHOD=trust -d postgres:13-alpine
	echo "Letting postgres warm up..."
	sleep 5
	docker exec pdl-sql psql -U postgres -c "DROP DATABASE airline" || true
	docker exec pdl-sql psql -U postgres -c "CREATE DATABASE airline"
	date
	python main.py -vv --weeks 1 "postgresql://postgres@localhost:5555/airline"
	date


define BUILD
date && env/bin/python main.py --weeks 2 "postgresql://postgres@localhost/airline" && date
endef
export BUILD

local:
	psql -U postgres -c "DROP DATABASE airline" || true
	psql -U postgres -c "CREATE DATABASE airline"
	echo "$(BUILD)" > ./.build-db.sh
	chmod +x ./.build-db.sh
	./.build-db.sh &> build.log &
	echo "Started Build"

clean:
	rm data.sqlite3 build.log || true
