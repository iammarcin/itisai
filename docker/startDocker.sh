#!/bin/bash

if [ $HOSTNAME == 'sherlock' ]; then
  . /home/ubuntu/.profile
  echo sherlock
  export NODE_ENV=sherlock
  docker-compose -f docker-compose.yml --env-file .env.sherlock down
  docker-compose -f docker-compose.yml --env-file .env.sherlock up
else
  source ~/.bash_profile
  echo local
  export NODE_ENV=local
  docker-compose -f docker-compose.local.yml --env-file .env.local down
  docker-compose -f docker-compose.local.yml --env-file .env.local up
fi
