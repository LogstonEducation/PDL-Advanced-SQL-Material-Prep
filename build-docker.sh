export DBPORT=5555
docker kill pdl-sql
docker rm pdl-sql
docker run --name pdl-sql -p $DBPORT:5432 -d postgres:latest
sleep 5
./build-db.sh &> db-build.log &

