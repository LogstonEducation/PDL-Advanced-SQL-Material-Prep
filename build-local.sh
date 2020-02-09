export DBPORT=5432
psql -U postgres -c "DROP DATABASE airline"
psql -U postgres -c "CREATE DATABASE airline"
./build-db.sh &> db-build.log &

