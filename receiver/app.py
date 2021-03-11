import connexion
import json
import os
from connexion import NoContent
from json.decoder import JSONDecodeError
import requests
import yaml
import logging
import logging.config
import datetime
from pykafka import KafkaClient

logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

hostname = app_config['events']['hostname']
port = app_config['events']['port']
topic_from_config = app_config['events']['topic']

MAX_EVENTS = 10
EVENT_FILE = 'events.json'

events_list = []

def report_weight_reading(body):
    logger.info(f"Received event Weight request with a unique id of {body['user_id']}")
    client = KafkaClient(hosts=f"{hostname}:{port}")
    topic = client.topics[str.encode(topic_from_config)]
    producer = topic.get_sync_producer()

    msg = { "type": "weight", 
            "datetime":   
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"), 
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    
    logger.info(f"Returned event Weight response (Id: {body['user_id']}) with status code 201")
    return NoContent, 201

def report_calories_reading(body):
    logger.info(f"Received event Calories request with a unique id of {body['user_id']}")
    client = KafkaClient(hosts=f"{hostname}:{port}")
    topic = client.topics[str.encode(topic_from_config)]
    producer = topic.get_sync_producer()

    msg = { "type": "calories", 
            "datetime":   
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"), 
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    
    logger.info(f"Returned event Calories response (Id: {body['user_id']}) with status code 201")
    return NoContent, 201

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("lab1openapi.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)