#Création des variables pour les tests en bash
export MONGO_INITDB_ROOT_USERNAME="root"
export MONGO_INITDB_ROOT_PASSWORD="root2024"
export ME_CONFIG_MONGODB_ADMINUSERNAME="root"
export ME_CONFIG_MONGODB_ADMINPASSWORD="root2024"
#création des variables pour docker-compose
echo "MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME}" > .env
echo "MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD}" >> .env
echo "ME_CONFIG_MONGODB_ADMINUSERNAME=${ME_CONFIG_MONGODB_ADMINUSERNAME}" >> .env
echo "ME_CONFIG_MONGODB_ADMINPASSWORD=${ME_CONFIG_MONGODB_ADMINPASSWORD}" >> .env
# Execution du pipeline avec docker compose
docker-compose --build --no-cache
docker-compose up -d