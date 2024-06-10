#!/bin/bash

if [ $HOSTNAME == 'sherlock' ] || [ $HOSTNAME == 'watson' ]; then
  . /home/nichu/.profile
  echo sherlock watson
  export NODE_ENV=sherlock
  docker-compose -f docker-compose.phpmyadmin.yml --env-file .env.sherlock down
  docker-compose -f docker-compose.phpmyadmin.yml --env-file .env.sherlock up
elif [ $HOSTNAME == 'ip-172-31-8-221' ]; then
  . /home/ubuntu/.profile
  echo atamaibiz
  export NODE_ENV=production
  docker-compose -f docker-compose.phpmyadmin.yml --env-file .env.atamaibiz down
  docker-compose -f docker-compose.phpmyadmin.yml --env-file .env.atamaibiz up # >> /c/docker/storage-common/testApi/logs/docker.sh.log 2>&1
else
  source ~/.bash_profile
  echo local
  export NODE_ENV=local
  echo "Don't start it here !"
fi
