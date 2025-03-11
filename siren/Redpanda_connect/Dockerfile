# Use the Redpanda Connect base image
FROM docker.redpanda.com/redpandadata/connect
# Switch to root to install certificates

# Copy CA certificates to the trusted directory
# COPY UniservTrustedFirepowerCA.crt /usr/local/share/ca-certificates/
# COPY winprditscert-root-cer-ohne-pkey.crt /usr/local/share/ca-certificates/
# RUN mkdir -p /etc/ssl/certs
# COPY ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
# Create directory structure with proper permissions
#Switch back to non-root user (UID 1000)
