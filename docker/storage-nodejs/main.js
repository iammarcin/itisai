'use strict';

const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const logger = require('./winston.js');
const awsRoute = require('./awsRoute');
const dbRoute = require('./dbRoute');
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

/* AWS */
app.post("/api/sendToS3",awsRoute.sendToS3);

/* DB */
app.post("/api/createChatSession",dbRoute.createChatSession);
app.post("/api/addMessageToChatSession",dbRoute.addMessageToChatSession);
app.get("/api/getUsersChats", dbRoute.getUsersChats);
app.post("/api/newMessageInChat", dbRoute.newMessageInChat);

app.listen(3000, function () {
    logger.info('Environment: ' + process.env.NODE_ENV);
    logger.info('server running on port 3000');
})
