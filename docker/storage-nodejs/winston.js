'use strict';

// this is commonjs module only
const {transports, createLogger, format} = require('winston');
const { prettyPrint } = format;

const levels = {
    error: 0,
    warn: 1,
    info: 2,
    verbose: 3,
    debug: 4,
    silly: 5
};

var logger = createLogger({
    format: format.combine(
        format.timestamp(),
        format.json(),
        prettyPrint()
    ),
    transports: [
        new transports.File({
            level: 'info',
            filename: '/tmp/winston.log',
            handleExceptions: true,
            json: true,
            maxsize: 5024288, //5MB
            maxFiles: 5,
            colorize: false
        }),
        new transports.Console({
            level: 'info',
            handleExceptions: true,
            json: true,
            colorize: true
        })
    ],
    exitOnError: false
});

module.exports = logger;

