#!/bin/bash

docker system prune -f 
docker system prune -f --all
docker system prune -f --volumes --all
docker rm -vf $(docker ps -aq)
docker rmi -f $(docker images -aq)
docker volume prune -f --all

# build only fastapi
# docker-compose -f docker-compose.local.yml --env-file .env.local build fastapibackend
