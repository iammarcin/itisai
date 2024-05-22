'use strict';

var settings = require('./nodejs_settings.js');
const logger = require("./winston.js");

//const mysql = require('mysql2/promise');
const mysql = require('mysql2');

const pool = mysql.createPool({
    host: settings.MYSQL_HOST,
    user: settings.MYSQL_USER,
    password: settings.MYSQL_PASS,
    database: settings.MYSQL_DB,
    //connectTimeout: 1000,
    //connectionLimit: 100,
});

const promisePool = pool.promise()

async function executeQuery(query, values = null) {
    //console.log("executeQuery triggered!");
    //const connection = await pool.getConnection();

    var queryOutput;
    var queryDetails;

    try {
        [queryOutput,queryDetails] = await promisePool.query(query, values);
        //connection.release();
        //pool.end();
    } catch(err) {
        if (settings.DEBUG == 1) {
            console.error("executeQuery error mysql.query");
            console.error(err);
        }
        throw Error(err);
    }

    if (settings.VERBOSE_SUPERB == 1) {
        logger.info("SUPER DEBUG VERBOSE_SUPERB ON");
        logger.info("DB Query " + query);
        logger.info("Query executed. Output: ");
        logger.info(JSON.stringify(queryOutput));
    }

    return queryOutput
  }

module.exports.executeQuery = executeQuery;


