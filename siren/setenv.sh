#Création des variables pour les tests en bash
export MYDIR=$(pwd)
export REDPANDA="$MYDIR/Redpanda"
export FILESIREN="$MYDIR/Files_Siren"
export NETWORK_DOCKER="siren_network"
export USERTABLEJOIN="$MYDIR/UserTable_Join"
export PGADMIN_DEFAULT_EMAIL="dataeng@gmail.com"
export PGADMIN_DEFAULT_PASSWORD="team2024"
export POSTGRES_USER="admin"
export POSTGRES_PASSWORD="team2024"
export POSTGRES_DB="siren"
export POSTGRES_DB_USER="user_api"
export POSTGRES_PORT="5432"
export ADMIN_USERNAME="apiadmin"
export ADMIN_MAIL="admin@gmail.com"
export ADMIN_PASSWORD="dataeng24"
export GF_SECURITY_ADMIN_USER="admin"
export GF_SECURITY_ADMIN_PASSWORD="adminpwd"
export VOLUME="dataengsiren"
export POSTGRES_HOST="192.168.1.59"
export IPHOST="192.168.1.59"
# création des variables pour la mise à jour quotidienne des données SIREN
export api_key="1e82a3c5-03d1-4e96-82a3-c503d12e963d"
export SECRET_KEY="a2ea064c916379d45b3c60c39ae8bd0df5c4f29cf0d87c58287a8462e5ae785a"
# Variables USER:GROUP pour DOCKER
# export U=$(id -u)
# export G=$(id -g)
# Yassin export API_KEY = "06871a5f-3654-469d-871a-5f3654869d10"
# export POSTGRES_HOST="postgres"
# POSTGRES_PORT="5432", Already in line 20
# POSTGRES_DB="siren", already in line 11
# POSTGRES_USER="admin", already in line 9
# POSTGRES_PASSWORD="team@2024" already in line 10
# PYTHONPATH=/Desktop/DATASCIENTEST/Project_Siren_Siret_data/Siren_project_yass/app
#volume pour utilisation dans le container
#if ! docker volume inspect $VOLUME > /dev/null 2>&1; then
#  docker volume create --name $VOLUME
#fi
#définition du réseau pour la communication entre les pipelines
# if ! docker network inspect postgre17_network > /dev/null 2>&1; then
#   docker network create postgre17_network
if ! docker network inspect $NETWORK_DOCKER > /dev/null 2>&1; then
  docker network create $NETWORK_DOCKER

fi
if [ ! -d "$FILESIREN" ]; then
  echo "Le répertoire $FILESIREN n'existe pas. Création en cours..."
  mkdir -p "$FILESIREN"
fi
#création des variables pour docker-compose
echo "MYDIR=$(pwd)" > .env
echo "REDPANDA=${REDPANDA}" >> .env
echo "FILESIREN=${FILESIREN}" >> .env
echo "NETWORK_DOCKER=${NETWORK_DOCKER}" >> .env
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
echo "GF_SECURITY_ADMIN_USER=${GF_SECURITY_ADMIN_USER}" >> .env
echo "GF_SECURITY_ADMIN_PASSWORD=${GF_SECURITY_ADMIN_PASSWORD}" >> .env
echo "IPHOST=${IPHOST}" >> .env
echo "POSTGRES_HOST=${POSTGRES_HOST}" >> .env
echo "api_key=${api_key}" >> .env
echo "POSTGRES_PORT=${POSTGRES_PORT}" >> .env
echo "SIREN_DATABASE_URL=\"postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}\"" >> .env
echo "USER_API_DATABASE_URL=\"postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB_USER}\"" >> .env
echo "SECRET_KEY=${SECRET_KEY}" >> .env
# # création des variables pour la mise à jour quotidienne des données SIREN
# echo "API_KEY=${API_KEY}" >> .env
# # Yassin export API_KEY = "06871a5f-3654-469d-871a-5f3654869d10"
# echo "POSTGRES_HOST=${POSTGRES_HOST}" >> .env
# POSTGRES_PORT="5432", Already in line 20
# POSTGRES_DB="siren", already in line 11
# POSTGRES_USER="admin", already in line 9
# POSTGRES_PASSWORD="team@2024" already in line 10
# PYTHONPATH=/Desktop/DATASCIENTEST/Project_Siren_Siret_data/Siren_project_yass/app
# Variables USER:GROUP pour DOCKER
# echo "U=${U}" >> .env
# echo "G=${G}" >> .env
cp .env ./data_updater
cp .env ./data_updater/app
cp .env ./Redpanda_connect
cp .env ./Redpanda
cp .env ./UserTable_Join
cp .env ./fastapi_project
cp .env ./ml_siren
# Execution du pipeline avec docker compose
#Pour générerer le container personnel avec redpanda-connect- Ceci permettra aussi de génerer des certificats dans le container
docker-compose build redpanda-connect-custom 
docker-compose build --no-cache
docker-compose up -d