FROM python:3.12-slim

# Install nginx supervisor and gettext
RUN apt-get update                              && \
    apt-get install -y --no-install-recommends  \
    nginx                                       \
    supervisor                                  \
    gettext                                     && \
    apt-get clean                               && \
    rm -rf /var/lib/apt/lists/*
