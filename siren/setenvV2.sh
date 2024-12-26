#Création des variables pour les tests en bash
export MYDIR=$(pwd)
export REDPANDA="$MYDIR/Redpanda"
export FILESIREN="$MYDIR/Files_Siren"
export PGADMIN_DEFAULT_EMAIL="dataeng@gmail.com"
export PGADMIN_DEFAULT_PASSWORD="team2024"
export POSTGRES_USER="admin"
export POSTGRES_PASSWORD="team2024"
export POSTGRES_DB="siren"
export VOLUME="dataengsiren"
export IPHOST="192.168.1.28"
export MONGO_INITDB_ROOT_USERNAME="root"
export MONGO_INITDB_ROOT_PASSWORD="root2024"
export ME_CONFIG_MONGODB_ADMINUSERNAME="root"
export ME_CONFIG_MONGODB_ADMINPASSWORD="root2024"
#création des variables pour docker-compose
echo "MYDIR=$(pwd)" > .env
echo "REDPANDA=${REDPANDA}" >> .env
echo "FILESIREN=${FILESIREN}" >> .env
echo "VOLUME=${VOLUME}" >> .env
echo "PGADMIN_DEFAULT_EMAIL=${PGADMIN_DEFAULT_EMAIL}" >> .env
echo "PGADMIN_DEFAULT_PASSWORD=${PGADMIN_DEFAULT_PASSWORD}" >> .env
echo "POSTGRES_USER=${POSTGRES_USER}" >> .env
echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" >> .env
echo "POSTGRES_DB=${POSTGRES_DB}" >> .env
echo "IPHOST=${IPHOST}" >> .env
echo "MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME}" >> .env
echo "MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD}" >> .env
echo "ME_CONFIG_MONGODB_ADMINUSERNAME=${ME_CONFIG_MONGODB_ADMINUSERNAME}" >> .env
echo "ME_CONFIG_MONGODB_ADMINPASSWORD=${ME_CONFIG_MONGODB_ADMINPASSWORD}" >> .env
cp .env ./Redpanda