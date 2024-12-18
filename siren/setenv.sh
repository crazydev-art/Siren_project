#Creátion des variables pour les tests en bash
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
#volume pour utilisation dans le container
if ! docker volume inspect $VOLUME > /dev/null 2>&1; then
  docker volume create --name $VOLUME
fi
#définition du réseau pour la communication entre les pipelines
if ! docker network inspect postgre17_network > /dev/null 2>&1; then
  docker network create postgre17_network
fi
if [ ! -d "$FILESIREN" ]; then
  echo "Le répertoire $FILESIREN n'existe pas. Création en cours..."
  mkdir -p "$FILESIREN"
fi
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
cp .env ./Redpanda
# Execution du pipeline avec docker compose
docker-compose up --build -d