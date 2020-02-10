sqlite:
	date
	python main.py "sqlite:///data.sqlite3"
	date

docker:
	docker kill pdl-sql || true
	docker rm pdl-sql || true
	docker run --name pdl-sql -p 5555:5432 -d postgres:latest
	sleep 5
	docker exec pdl-sql psql -U postgres -c "DROP DATABASE airline" || true
	docker exec pdl-sql psql -U postgres -c "CREATE DATABASE airline"
	date
	pipenv run python main.py "postgresql://postgres@localhost:5555/airline"
	date

local:
	psql -U postgres -c "DROP DATABASE airline" || true
	psql -U postgres -c "CREATE DATABASE airline"
	source env/bin/activate
	cat > ./build-db.sh <<EOF
		date
		python main.py "postgresql://postgres@localhost:/airline"
		date
	EOF
	./build-db.sh &> build.log &

clean:
	rm data.sqlite3 build.log
