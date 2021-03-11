import connexion
from connexion import NoContent

import json
import os
from json.decoder import JSONDecodeError

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import mysql.connector

from base import Base
from weight import Weight
from calories import Calories
import datetime

import yaml
import logging
import logging.config

from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

logger = logging.getLogger('basicLogger')

with open('app_config.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

user = app_config['datastore']['user']
password = app_config['datastore']['password']
hostname = app_config['datastore']['hostname']
port = app_config['datastore']['port']
db = app_config['datastore']['db']

DB_ENGINE = create_engine(f"mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info(f"Connecting to DB. Hostname: {hostname}, port: {port}")

def report_weight_reading(body):
    """ Receives a weight reading """

    session = DB_SESSION()

    w = Weight(body['user_id'],
               body['user_name'],
               body['weight'],
               body['timestamp'])
    session.add(w)

    session.commit()
    session.close()

    logger.debug(f"Stored event Weight request with a unique id of {body['user_id']}")

def report_calories_reading(body):
    """ Receives a calories reading """

    session = DB_SESSION()

    c = Calories(body['user_id'],
                 body['user_name'],
                 body['calories'],
                 body['timestamp'])

    session.add(c)

    session.commit()
    session.close()

    logger.debug(f"Stored event Calories request with a unique id of {body['user_id']}")

    
def get_weight_readings(timestamp):
    """ Gets new weight readings after the timestamp """
    session = DB_SESSION()
    
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    print(timestamp_datetime)
    
    readings = session.query(Weight).filter(Weight.date_created>= timestamp_datetime)
    
    results_list = []
    
    for reading in readings:
        results_list.append(reading.to_dict())
        
    session.close()
    
    logger.info("Query for Weight readings after %s returns %d results" % 
                (timestamp, len(results_list)))
                
    return results_list, 200

def get_calories_readings(timestamp):
    """ Gets new calories readings after the timestamp """
    session = DB_SESSION()
    
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    print(timestamp_datetime)
    
    readings= session.query(Calories).filter(Calories.date_created>= timestamp_datetime)
    
    results_list = []
    
    for reading in readings:
        results_list.append(reading.to_dict())
        
    session.close()
    
    logger.info("Query for Calories readings after %s returns %d results" % 
                (timestamp, len(results_list)))
                
    return results_list, 200

def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    # Create a consume on a consumer group, that only reads new messages 
    # (uncommitted messages) when the service re-starts (i.e., it doesn't 
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    # This is blocking -it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "weight": # Change this to your event type
            logger.info("Storing weight event to the database")
            report_weight_reading(payload)
        elif msg["type"] == "calories": # Change this to your event type
            logger.info("Storing calories event to the database")
            report_calories_reading(payload)
        
        # Commit the new message as being read
        consumer.commit_offsets()

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("lab1openapi.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start() 
    app.run(port=8090)