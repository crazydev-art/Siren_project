
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg-agent \
        software-properties-common

RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
    apt-get update

RUN apt-get install -y --no-install-recommends \
        docker-ce-cli docker-ce && \
    rm -rf /var/lib/apt/lists/*

# Set the container to run as root
# USER root # modified 19.12.2024#

#User external ENV during Build of container
ARG MYDIR
ARG REDPANDA
ARG FILESIREN
ARG IPHOST
ARG NETWORK_DOCKER

# Define REDPANDA environment variable - .env over docker-compose
ENV MYDIR=${MYDIR}
ENV REDPANDA=${REDPANDA}
ENV FILESIREN=${FILESIREN}
ENV IPHOST=${IPHOST}
ENV NETWORK_DOCKER=${NETWORK_DOCKER}

# Copy files to the container
COPY *.yaml $REDPANDA/
COPY .env $REDPANDA/
COPY siren_de.sh $REDPANDA/siren_de.sh
RUN chmod +x $REDPANDA/siren_de.sh

# RUN mkdir -p $REDPANDA/Files_Siren/ #modified 19.12.2024


# Set the working directory
WORKDIR $REDPANDA

# Start Docker daemon and run the script
# Run the Docker daemon as a background process
CMD ["./siren_de.sh"]