#Création des variables pour le déploiement container/Redpanda/Prometheus
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
export ADMIN_USERNAME="apiadmin"
export ADMIN_MAIL="admin@gmail.com"
export ADMIN_PASSWORD="dataeng24"
export GF_SECURITY_ADMIN_USER="admin"
export GF_SECURITY_ADMIN_PASSWORD="adminpwd"
export VOLUME="dataengsiren"
export IPHOST="192.168.1.59"
export POSTGRES_PORT="5432"
export MONGO_INITDB_ROOT_USERNAME="root"
export MONGO_INITDB_ROOT_PASSWORD="root2024"
export ME_CONFIG_MONGODB_ADMINUSERNAME="root"
export ME_CONFIG_MONGODB_ADMINPASSWORD="root2024"
# création des variables pour la mise à jour quotidienne des données SIREN
export API_KEY="1e82a3c5-03d1-4e96-82a3-c503d12e963d"
# Yassin export API_KEY = "06871a5f-3654-469d-871a-5f3654869d10"
export POSTGRES_HOST="postgres"
# POSTGRES_PORT="5432", Already in line 20
# POSTGRES_DB="siren", already in line 11
# POSTGRES_USER="admin", already in line 9
# POSTGRES_PASSWORD="team@2024" already in line 10
# PYTHONPATH=/Desktop/DATASCIENTEST/Project_Siren_Siret_data/Siren_project_yass/app

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
echo "POSTGRES_PORT=${POSTGRES_PORT}" >> .env
echo "MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME}" >> .env
echo "MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD}" >> .env
echo "ME_CONFIG_MONGODB_ADMINUSERNAME=${ME_CONFIG_MONGODB_ADMINUSERNAME}" >> .env
echo "ME_CONFIG_MONGODB_ADMINPASSWORD=${ME_CONFIG_MONGODB_ADMINPASSWORD}" >> .env
# création des variables pour la mise à jour quotidienne des données SIREN
echo "API_KEY=${API_KEY}" >> .env
# Yassin export API_KEY = "06871a5f-3654-469d-871a-5f3654869d10"
echo "POSTGRES_HOST=${POSTGRES_HOST}" >> .env
# POSTGRES_PORT="5432", Already in line 20
# POSTGRES_DB="siren", already in line 11
# POSTGRES_USER="admin", already in line 9
# POSTGRES_PASSWORD="team@2024" already in line 10
# PYTHONPATH=/Desktop/DATASCIENTEST/Project_Siren_Siret_data/Siren_project_yass/app
cp .env ../data_updater_2/app/
cp .env ./Redpanda_connect
cp .env ./Redpanda
cp .env ./UserTable_Join
