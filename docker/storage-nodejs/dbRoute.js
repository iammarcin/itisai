'use strict';

const settings = require('./nodejs_settings.js');
const logger = require("./winston.js");
const dbClient = require('./db-client.js');
const uuid = require('uuid');

// generate unique id for chat session
const generateUniqueId = () => {
    return uuid.v4();
};

async function createChatSession(req, res) {
  try {
      const sessionId = generateUniqueId();
      const customerId = req.body.customerId;
      const query = "INSERT INTO `chat_sessions` (`customerId`, `sessionId`) VALUES ('"+customerId+"', '"+sessionId+"');"

      if (settings.DEBUG == 1) {
          logger.info("createChatSession triggered!!!!!!");
          logger.info(req.body);
          logger.info("SQL: " + query);
      }

      /* for update query not using cache */
      const result = await dbClient.executeQuery(query, 0);
      res.status(200).send({ "code": 200, "success": true, "message": result.info, "Time": Date.now() });

  } catch (e) {
      if (settings.DEBUG == 1) {
          logger.error(e);
          logger.error(Date.now());
      }
      res.status(400).send( { "code": 400, "success": false, "message": 'createChatSession '+e, "Time": Date.now()  } );
  }
}

async function addMessageToChatSession(req, res) {
  try {
      const customerId = req.body.customerId;
      const sessionId = req.body.sessionId;
      const requestId = req.body.requestId;
      const query = "INSERT INTO `chat_messages` (`customerId`, `sessionId`, `requestId`) VALUES ('"+customerId+"', '"+sessionId+"', , '"+requestId+"');"
      if (settings.DEBUG == 1) {
          logger.info("addMessageToChatSession triggered!!!!!!");
          logger.info(req.body);
          logger.info("SQL: " + query);
      }

      /* for update query not using cache */
      const result = await dbClient.executeQuery(query, 0);
      res.status(200).send({ "code": 200, "success": true, "message": result.info, "Time": Date.now() });

  } catch (e) {
      if (settings.DEBUG == 1) {
          logger.error(e);
          logger.error(Date.now());
      }
      res.status(400).send( { "code": 400, "success": false, "message": 'addMessageToChatSession '+e, "Time": Date.now()  } );
  }
}

async function getUsersChats(req, res) {
  try {
      const customerId = req.query.customerId ? req.query.customerId : 0;
      const limit = req.query.limit ? parseInt(req.query.limit) : 10;
      const offset = req.query.offset ? parseInt(req.query.offset) : 0;

      const query = "SELECT \
          chat_sessions.id, chat_sessions.title, latest_request.assetInput \
          FROM chat_sessions \
          JOIN chat_messages ON chat_sessions.id = chat_messages.sessionId \
          JOIN requests latest_request ON chat_messages.requestId = latest_request.id \
          WHERE chat_sessions.customerId = "+customerId+" \
          AND latest_request.lastUpdate = ( \
              SELECT MAX(lastUpdate) \
              FROM requests \
              JOIN chat_messages ON requests.id = chat_messages.requestId \
              WHERE chat_messages.sessionId = chat_sessions.id \
          ) \
          ORDER BY chat_sessions.lastUpdate DESC, chat_sessions.started DESC  \
          LIMIT "+limit+" OFFSET "+offset+";";
      logger.info("!!!!!")
      logger.info(query)
      const result = await dbClient.executeQuery(query, 0);

      res.status(200).send({ "code": 200, "success": true, "message": result , "Time": Date.now() });
  } catch (e) {
      if (settings.DEBUG == 1) {
          logger.error(e);
          logger.error(Date.now());
      }
      res.status(400).send( { "code": 400, "success": false, "message": 'getUsersChats '+e, "Time": Date.now()  } );
  }
}

async function newMessageInChat(req, res) {
  try {
      const customerId = req.body.customerId;
      const category = req.body.category;
      const action = req.body.action;
      const userInput = JSON.stringify(req.body.userInput);
      const assetInput = JSON.stringify(req.body.assetInput);
      const userSettings = JSON.stringify(req.body.userSettings);
      const generatorJobId = "null";
      // this is to check the fact if its new session or maybe already existing
      // set to true if new session or false if not
      const newSession = req.body.newSession ? req.body.newSession : 0;

      // if there is new session, use exisitng session id
      let sessionId;
      if (newSession == true) {
          sessionId = generateUniqueId();
      } else {
          sessionId = JSON.parse(userInput)['sessionId'];
      }

      console.log("sessionId = " + sessionId);

      const query = `CALL newMessageInChat(?, ?, ?, ?, ?, ?, ?, ?, ?, @newRequestId);`;

      const values = [customerId, category, action, userInput, assetInput, userSettings, generatorJobId, newSession, sessionId];

      if (settings.DEBUG == 1) {
          logger.debug("newMessageInChat triggered!!!!!!");
      }

      /* for update query not using cache */
      const result = await dbClient.executeQuery(query, values, 0);

      if (settings.VERBOSE_SUPERB == 1) {
          console.log("!!!")
          logger.info(req.body);
          logger.info("SQL: " + query);
          logger.info("SQL values: " + values);
          console.log(result)
          console.log(result[0])
          console.log(result[0][0])
      }
      const newRequestId = result[0][0]['newRequestId'];
      const newSessionId = result[0][0]['sessionId'] ? result[0][0]['sessionId'] : null;

      res.status(200).send({ "code": 200, "success": true, "message": { "newRequestId": newRequestId, "sessionId": newSessionId } , "Time": Date.now() });

  } catch (e) {
      if (settings.DEBUG == 1) {
          logger.error(e);
          logger.error(Date.now());
      }
      res.status(400).send( { "code": 400, "success": false, "message": 'newMessageInChat '+e, "Time": Date.now()  } );
  }
}

module.exports.createChatSession = createChatSession;
module.exports.addMessageToChatSession = addMessageToChatSession;
module.exports.getUsersChats = getUsersChats;
module.exports.newMessageInChat = newMessageInChat;
