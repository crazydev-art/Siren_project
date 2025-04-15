FROM node:18

WORKDIR /projet-dst
# Copy files to the container
COPY . .

#User external ENV during Build of container
ARG MYDIR
ARG USERTABLEJOIN
ARG POSTGRES_USER
ARG NETWORK_DOCKER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DB
ARG POSTGRES_DB_USER
ARG ADMIN_USERNAME
ARG ADMIN_MAIL
ARG ADMIN_PASSWORD
ARG SIREN_DATABASE_URL
ARG USER_API_DATABASE_URL
ARG SECRET_KEY
ARG IPHOST
ARG VITE_FAST_API_URL
ARG fast_api_url

# Define nvm environment variable - .env over docker-compose
ENV SIREN_DATABASE_URL=${SIREN_DATABASE_URL}
ENV USER_API_DATABASE_URL=${USER_API_DATABASE_URL}
ENV IPHOST=${IPHOST}
ENV SECRET_KEY=${SECRET_KEY}
ENV VITE_FAST_API_URL=${VITE_FAST_API_URL}
ENV fast_api_url=${fast_api_url}
# Define REDPANDA environment variable - .env over docker-compose
ENV MYDIR=${MYDIR}
ENV USERTABLEJOIN=${USERTABLEJOIN}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV NETWORK_DOCKER=${NETWORK_DOCKER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}
ENV POSTGRES_DB_USER=${POSTGRES_DB_USER}
ENV ADMIN_USERNAME=${ADMIN_USERNAME}
ENV ADMIN_MAIL=${ADMIN_MAIL}
ENV ADMIN_PASSWORD=${ADMIN_PASSWORD}

# Set the working directory
WORKDIR /projet-dst/project

RUN npm install vite --save-dev
RUN npm install @headlessui/react
RUN npm audit fix --force
RUN npx update-browserslist-db@latest

EXPOSE 5173

# Start Docker daemon and run the script
# Run the Docker daemon as a background process
CMD ["sh", "-c", "npm run dev -- --host"]