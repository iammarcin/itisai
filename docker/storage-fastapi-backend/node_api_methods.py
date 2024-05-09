import traceback
import requests
import config
import logconfig
logger = logconfig.logger

node_api_endpoint = config.defaults['NODE_API_ENDPOINT']

def update_request_status(
    customerId = 1, 
    endpoint = "", 
    status = "", 
    category = "", 
    action = "", 
    userInput = "", 
    requestId=None, generatorJobId=None):
    try:
        myJson = {}
        if endpoint == "createRequest":
            myJson={
                "customerId": customerId,
                "category": category,
                "action": action,
                "userInput": userInput,
                "generatorJobId": generatorJobId,
                "status": status,
            }
        elif endpoint == "updateRequest":
            myJson={
                "requestId": requestId,
                "generatorJobId": generatorJobId,
                "status": status,
            }
        response = requests.post(node_api_endpoint + "/" + endpoint, json=myJson)

        logger.info("update_request_status result: " + str(response))
        return response.json()        
    except Exception as e:
        logger.error("Error in update_request_status")
        logger.error(e)
        traceback.print_exc()
