'use strict';

const config = {};
config.mysql = {};

if (process.env.NODE_ENV == 'production') {
    config.AWS_REGION = 'eu-west-1';
    config.AWS_S3_BUCKET = "myaiapps3bucket";
    config.MYSQL_HOST = "dbai.cvccw8kacdjk.eu-west-1.rds.amazonaws.com"
    config.MYSQL_USER = "aitools"
    config.MYSQL_PASS = process.env.AWS_DB_PASS
    config.MYSQL_DB = "content"
} else { // local docker
    config.AWS_REGION = 'eu-west-1';
    config.AWS_S3_BUCKET = "myaiapps3bucket";
    config.MYSQL_HOST = "dbai.cvccw8kacdjk.eu-west-1.rds.amazonaws.com"
    config.MYSQL_USER = "aitools"
    config.MYSQL_PASS = process.env.AWS_DB_PASS
    config.MYSQL_DB = "content_nonprod"
}

config.DEBUG = 1;
config.VERBOSE_SUPERB = 0;

// this is used in awsRoute to s3 upload
config.ALLOWED_FILE_TYPES = "jpg|jpeg|png|mp3|mpeg|mpga|webm|wav|m4a|txt|mp4";

module.exports = config;
