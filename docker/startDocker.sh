#!/bin/bash

if [ $HOSTNAME == 'sherlock' ] || [ $HOSTNAME == 'watson' ]; then
  . /home/nichu/.profile
  echo sherlock watson
  export NODE_ENV=sherlock
  docker-compose -f docker-compose.yml --env-file .env.sherlock down
  docker-compose -f docker-compose.yml --env-file .env.sherlock up
elif [ $HOSTNAME == 'awsec2' ]; then
  . /home/ubuntu/.profile
  echo atamaibiz
  export NODE_ENV=production
  docker-compose -f docker-compose.prod.yml --env-file .env.atamaibiz down
  docker-compose -f docker-compose.prod.yml --env-file .env.atamaibiz up # >> /c/docker/storage-common/testApi/logs/docker.sh.log 2>&1
else
  source ~/.bash_profile
  echo local
  export NODE_ENV=local
  docker-compose -f docker-compose.local.yml --env-file .env.local down
  docker-compose -f docker-compose.local.yml --env-file .env.local up
fi
