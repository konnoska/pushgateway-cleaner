'''
A simple module that cleans pushgateway.
'''
import os
import logging as log
import re
from datetime import timedelta
from datetime import datetime
from functools import cache
import threading
import time
import requests


regex = re.compile(r'((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
log_level = {
             'DEBUG':   log.DEBUG,
             'INFO':    log.INFO,
             'WARNING': log.WARNING,
             'ERROR':   log.ERROR
            }


@cache
def get_config():
    '''
    Reads configuration from environment.
    '''
    config = {}
    config["expiration_duration"] = os.environ.get("CLEANER_EXPIRATION_DURATION","5m")
    config["cleaning_interval"] = os.environ.get("CLEANER_CLEANING_INTERVAL","1m")
    config["endpoint"] = os.environ.get('CLEANER_ENDPOINT','localhost:9091')
    config["path"]     = os.environ.get('CLEANER_PATH',"api/v1/metrics")
    config["log_lvl"]  = os.environ.get('CLEANER_LOG_LVL',"INFO")
    return config


@cache
def parse_time(time_str:str):
    '''
    Args:
        time_str (str): 1h10s
    Returns:
        timedelta:

    Examples:
        >>> parse_time('1h10s')
        >>> datetime.timedelta(seconds=3610)
    '''
    parts = regex.match(time_str)
    if not parts:
        raise Exception(f"Unknown time string: {time_str}")
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(float(param))
    return timedelta(**time_params)


def needs_deletion(timestamp):
    '''
    Check if the given timestamp is older
    than retention period.
    '''
    cfg = get_config()
    dt_timestamp = datetime.fromtimestamp(timestamp)
    if (datetime.now() - dt_timestamp ) > parse_time(cfg['expiration_duration']):
        return True
    return False

def get_group_path(group_labels:dict):
    '''
    Example:
        >>> get_group_path( {'job':'some_job', 'instance':'some_instance'} )
        >>> 'job/some_job/instance/some_instance'
    '''
    group_path = f"job/{group_labels.pop('job')}/"
    group_path += "/".join( \
                [f"{label_key}/{label_value}" for label_key,label_value in group_labels.items()]
            )
    return group_path

def delete_group(group_path:str):
    '''
    Deletes the metric group defined by the given path.
    Example:
        >>> delete_group("job/some_job/instance/some_instance")
    '''
    cfg = get_config()
    api = f"http://{cfg['endpoint']}/metrics/{group_path}"
    resp = requests.delete(api, timeout=10)
    resp.raise_for_status()


def clean():
    '''
    Get all the metric groups fomr the pushgateway,
    and deletes the expired ones.
    '''
    cfg = get_config()
    resp = requests.get(f"http://{cfg['endpoint']}/{cfg['path']}",timeout=10)
    resp.raise_for_status()
    parsed_resp = resp.json()

    for metric_group in parsed_resp['data']:

        last_push_timestamp = int(float(metric_group['push_time_seconds']['metrics'][0]['value']))
        group_labels = metric_group["labels"]
        group_path = get_group_path(group_labels)

        if needs_deletion(last_push_timestamp):
            log.info("DELETING %s - last_push: %s more than %s ago",
                    group_path,
                    datetime.fromtimestamp(last_push_timestamp),
                    cfg['expiration_duration'])
            delete_group(group_path)
        else:
            log.info("SKIPPING %s - last_push: %s less than %s ago",
                    group_path,
                    datetime.fromtimestamp(last_push_timestamp),
                    cfg['expiration_duration'])


if __name__ == "__main__":
    c = get_config()
    log.basicConfig(level=log_level[c['log_lvl']], format='%(asctime)s %(levelname)s: %(message)s')

    log.info(c)
    cleaning_interval = parse_time(c["cleaning_interval"])
    while True:
        t = threading.Thread(target=clean)
        t.start()
        t.join(timeout=10)
        log.debug("sleeping")
        time.sleep(cleaning_interval.seconds)
