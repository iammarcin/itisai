'use strict';

const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const logger = require('./winston.js');
const awsRoute = require('./awsRoute');
const settings = require('./nodejs_settings.js');

/**for frontend parser  */
app.use(bodyParser.urlencoded({
    extended: true
}));

/** for backend json parser*/
app.use(bodyParser.json());

app.use(function (req,res,next) {
    console.log("")
    console.log("Call URL: " + req.url)
    console.log("Method: " + req.method);
    console.log("Origin: " + req.headers.origin);
    if ( settings.VERBOSE_SUPERB == 1 && req.body ) {
        console.log("Params: " + req.body);
        console.dir(req.body);
    }
    next();
});

app.use(function (req, res, next) {
    // after changing ssl cert to wildcard - this is not needed anymore
    /*
    if (process.env.NODE_ENV == 'local') {

        if (req.headers.origin === "http://192.168.100.26:3000") {
            //res.header("Access-Control-Allow-Origin", req.headers.origin);
        } else {
            res.header("Access-Control-Allow-Methods", "GET, PUT, POST, DELETE");
            res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, x-access-token, Content-Type, Accept");
            res.header("Access-Control-Allow-Credentials", "true");
        }

        // Handle preflight requests
        if (req.method === "OPTIONS") {
            //res.header("Access-Control-Allow-Methods", "GET, PUT, POST, DELETE");
            return res.status(200).json({});
        }
    } else {
        // headers set in apache2 - when set here too - it was failing
        // Handle preflight requests
        if (req.method === "OPTIONS") {
            //res.header("Access-Control-Allow-Methods", "GET, PUT, POST, DELETE");
            return res.status(200).json({});
        }
    } */

    next();
});

/* AWS */
app.post("/api/sendToS3",awsRoute.sendToS3);


app.listen(3000, function () {
    logger.info('Environment: ' + process.env.NODE_ENV);
    logger.info('server running on port 3000');
})
