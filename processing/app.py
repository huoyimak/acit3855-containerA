import connexion
from connexion import NoContent

from apscheduler.schedulers.background import BackgroundScheduler

import json
import os
from json.decoder import JSONDecodeError


import yaml
import logging
import logging.config

from datetime import datetime
import requests

import os.path
from os import path

logger = logging.getLogger('basicLogger')

with open('app_config.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

def get_stats():
    """ Gets stats of both Weight and Calories """
    stats = {}
    logger.info("Request has started")
    json_file = app_config['datastore']['filename']
    if path.exists(json_file):
        with open(json_file, 'r') as file:
            stats = json.load(file)
    else:
        logger.error("Statistics do not exist")
        return NoContent, 404
    
    new_stats = {
        "num_weight_readings": stats['num_weight_readings'], 
        "max_weight_reading": stats['max_weight_reading'],
        "min_weight_reading": stats['min_weight_reading'],
        "num_calories_readings": stats['num_calories_readings'],
        "avg_calories_reading": stats['avg_calories_reading'],
        "last_updated": stats['last_updated']
    }
    logger.debug(f"Content of the dictionary: {new_stats}")
    logger.info("Request has completed")
    return new_stats, 200


def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic has started")
    json_file = app_config['datastore']['filename']
    data = {}
    # Get current stats
    if path.exists(json_file):
        with open(json_file, 'r') as file:
            data = json.load(file)
    else:
        # Populate file with default data
        with open(json_file, 'w') as file:
            data = {
                    "num_weight_readings": 0, 
                    "max_weight_reading": 0, 
                    "min_weight_reading": 99999, 
                    "num_calories_readings": 0, 
                    "avg_calories_reading": 0, 
                    "last_updated": datetime.strftime(datetime.min, "%Y-%m-%dT%H:%M:%SZ")
                    }
            json_data = json.dumps(data)
            file.write(json_data)

    # Update the stats with data since the last updated date
    updated_num_weight_readings = 0
    updated_max_weight_reading = 0
    updated_min_weight_reading = 99999
    updated_num_calories_readings = 0
    updated_avg_calories_reading = 0
    updated_last_updated = datetime.min

    current_datetime = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ")
    current_last_updated = data["last_updated"]

    print(current_last_updated)
    url = app_config["eventstore"]["url"]
    weight_response = requests.get(url + "/readings/weight", params = {"timestamp": current_last_updated})

    if weight_response.status_code == 200:
        weight_data = weight_response.json()
        logger.info(str(len(weight_data)) + " weight events received")

        updated_num_weight_readings = data["num_weight_readings"] + len(weight_data)

        current_max_weight = data["max_weight_reading"]
        for weight_event in weight_data:
            if weight_event["weight"] > current_max_weight:
                current_max_weight = weight_event["weight"]
        updated_max_weight_reading = current_max_weight

        current_min_weight = data["min_weight_reading"]
        for weight_event in weight_data:
            if weight_event["weight"] < current_min_weight:
                current_min_weight = weight_event["weight"]
        updated_min_weight_reading = current_min_weight

    else:
        logger.error("Received invalid response")

    calories_response = requests.get(url + "/readings/calories", params = {"timestamp": current_last_updated})

    if calories_response.status_code == 200:
        calories_data = calories_response.json()
        logger.info(str(len(calories_data)) + " calories events received")

        updated_num_calories_readings = data["num_calories_readings"] + len(calories_data)

        current_total_calories = data["avg_calories_reading"] * data["num_calories_readings"]
        for calories_event in calories_data:
            current_total_calories = current_total_calories + calories_event["calories"]

        updated_avg_calories_reading = current_total_calories / updated_num_calories_readings
    else:
        logger.error("Received invalid response")

    
    updated_last_updated = current_datetime

    updated_data = {
                    "num_weight_readings": updated_num_weight_readings, 
                    "max_weight_reading": updated_max_weight_reading, 
                    "min_weight_reading": updated_min_weight_reading, 
                    "num_calories_readings": updated_num_calories_readings, 
                    "avg_calories_reading": updated_avg_calories_reading, 
                    "last_updated": updated_last_updated
                    }
    updated_json_data = json.dumps(updated_data)
    with open(json_file, 'w') as file:
        file.write(updated_json_data)

    logger.debug(f"Current Statistics: {updated_json_data}")
    logger.info("Stats processing has ended")
    

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

with open('app_config.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("lab1openapi.yaml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    # run our standalone event server
    init_scheduler()
    app.run(port=8100, use_reloader=False)