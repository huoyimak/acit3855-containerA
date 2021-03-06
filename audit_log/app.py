import connexion
from connexion import NoContent

from pykafka import KafkaClient

import json
import yaml
import logging
import logging.config

logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

def get_weight_reading(index):
    """ Get weight Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], 
                          app_config["events"]["port"])                              
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue. 
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, 
                                        consumer_timeout_ms=1000)
    
    logger.info("Retrieving Weight at index %d" % index)
    try:
        counter = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            
            if msg["type"] == "weight":
                if counter == index:
                    return msg["payload"], 200
                else:
                    counter += 1
            
    except:
        logger.error("No more messages found")
        
    logger.error("Could not find weight at index %d" % index)
    return { "message": "Not Found"}, 404

def get_calories_reading(index):
    """ Get calories Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], 
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue. 
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, 
                                        consumer_timeout_ms=1000)
    
    logger.info("Retrieving Calories at index %d" % index)
    try:
        counter = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            
            if msg["type"] == "calories":
                if counter == index:
                    return msg["payload"], 200
                else:
                    counter += 1
            
    except:
        logger.error("No more messages found")
        
    logger.error("Could not find calories at index %d" % index)
    return { "message": "Not Found"}, 404

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)