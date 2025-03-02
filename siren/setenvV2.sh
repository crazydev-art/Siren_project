#Création des variables pour les tests en bash
export MYDIR=$(pwd)
export REDPANDA="$MYDIR/Redpanda"
export FILESIREN="$MYDIR/Files_Siren"
export USERTABLEJOIN="$MYDIR/UserTable_Join"
export PGADMIN_DEFAULT_EMAIL="dataeng@gmail.com"
export PGADMIN_DEFAULT_PASSWORD="team2024"
export POSTGRES_USER="admin"
export POSTGRES_PASSWORD="team2024"
export POSTGRES_DB="siren"
export POSTGRES_DB_USER="user_api"
export ADMIN_USERNAME="apiadmin"
export ADMIN_MAIL="admin@gmail.com"
export ADMIN_PASSWORD="dataeng24"
export VOLUME="dataengsiren"
export IPHOST="192.168.1.28"
export POSTGRES_PORT="5432"
export MONGO_INITDB_ROOT_USERNAME="root"
export MONGO_INITDB_ROOT_PASSWORD="root2024"
export ME_CONFIG_MONGODB_ADMINUSERNAME="root"
export ME_CONFIG_MONGODB_ADMINPASSWORD="root2024"
#création des variables pour docker-compose
echo "MYDIR=$(pwd)" > .env
echo "REDPANDA=${REDPANDA}" >> .env
echo "FILESIREN=${FILESIREN}" >> .env
echo "USERTABLEJOIN=${USERTABLEJOIN}" >> .env
echo "VOLUME=${VOLUME}" >> .env
echo "PGADMIN_DEFAULT_EMAIL=${PGADMIN_DEFAULT_EMAIL}" >> .env
echo "PGADMIN_DEFAULT_PASSWORD=${PGADMIN_DEFAULT_PASSWORD}" >> .env
echo "POSTGRES_USER=${POSTGRES_USER}" >> .env
echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" >> .env
echo "POSTGRES_DB=${POSTGRES_DB}" >> .env
echo "POSTGRES_DB_USER=${POSTGRES_DB_USER}" >> .env
echo "ADMIN_USERNAME=${ADMIN_USERNAME}" >> .env
echo "ADMIN_MAIL=${ADMIN_MAIL}" >> .env
echo "ADMIN_PASSWORD=${ADMIN_PASSWORD}" >> .env
echo "IPHOST=${IPHOST}" >> .env
echo "POSTGRES_PORT=${POSTGRES_PORT}" >> .env
echo "MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME}" >> .env
echo "MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD}" >> .env
echo "ME_CONFIG_MONGODB_ADMINUSERNAME=${ME_CONFIG_MONGODB_ADMINUSERNAME}" >> .env
echo "ME_CONFIG_MONGODB_ADMINPASSWORD=${ME_CONFIG_MONGODB_ADMINPASSWORD}" >> .env
cp .env ./Redpanda
cp .env ./UserTable_Join