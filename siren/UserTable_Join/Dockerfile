FROM python:3.9-slim

#User external ENV during Build of container
ARG MYDIR
ARG USERTABLEJOIN
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB
ARG IPHOST
ARG POSTGRES_DB_USER
ARG ADMIN_USERNAME
ARG ADMIN_MAIL
ARG ADMIN_PASSWORD

# Define REDPANDA environment variable - .env over docker-compose
ENV MYDIR=${MYDIR}
ENV USERTABLEJOIN=${USERTABLEJOIN}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}
ENV IPHOST=${IPHOST}
ENV POSTGRES_DB_USER=${POSTGRES_DB_USER}
ENV ADMIN_USERNAME=${ADMIN_USERNAME}
ENV ADMIN_MAIL=${ADMIN_MAIL}
ENV ADMIN_PASSWORD=${ADMIN_PASSWORD}

# Copie le fichier requirements en premier pour optimiser le cache Docker
COPY requirements.txt $USERTABLEJOIN/
# Copie des scripts Python dans le conteneur
COPY *.py $USERTABLEJOIN/

# Set the working directory
WORKDIR $USERTABLEJOIN/

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Start Docker daemon and run the script
# Run the Docker daemon as a background process
# Commande d'exécution des deux scripts (séquentielle)
CMD ["sh", "-c", "python user_table.py && python inner_join.py"]