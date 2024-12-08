export REDPANDA=$(pwd)
export DATAENGSIREN=$(dirname $(pwd))
export FILESIREN="$DATAENGSIREN/Files_Siren"
#création des variables pour docker-compose
echo "REDPANDA=$(pwd)" > .env
echo "DATAENGSIREN=$(dirname $(pwd))" >> .env
echo "FILESIREN=${FILESIREN}" >> .env