import time
import os
import math
from decimal import *
from random import randrange
import json
getcontext().prec = 17

import logging
log = logging.getLogger(__name__)


def date_now_milli():
    return time.time()
    

def write_session_dir(session_identifier):
    path = f'data/session_{session_identifier}/'

    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except OSError:
            # log.error("Creation of the directory %s failed" % path)
            path = 'data/'
        # else:
            # log.info("Successfully created the directory %s " % path)

    return path


def skip_round(session, round_number):
    if session.config['skip_to_round'] > round_number:
        return True


class TimeFormatter:
    """This class accepts seconds and returns MM:SS.ss since first event"""
    def __init__(self, start):
        self.start = start

    def format(self, time):
        t = time - self.start
        minutes = math.floor(t // 60)
        seconds = t % 60
        return "{}:{}".format(minutes, seconds)

def unformat_time(time):
    breakdown = time.split(':')
    minutes = int(breakdown[0])
    seconds = float(breakdown[1])
    if minutes:
        seconds += minutes*60

    return seconds


def average_harvest():
    harvest_times = []
    file_name = "harvest_test.csv"

    f = open(file_name, 'r', newline='')
    harvest_start=None
    harvest_end=None
    for index, x in enumerate(f):
        columns = x.split(',')
        time = unformat_time(columns[22])

        harvest_status = int(columns[30])

        if index == 0:
            harvest_start = time

        if harvest_status != 4:
            continue

        if harvest_status == 4:
            harvest_end=time
            harvest_time = harvest_end-harvest_start
            harvest_times.append(harvest_time)
            harvest_start=harvest_end
        else:
            print('ERROR')

    # calculate averate
    total_time = 0
    total = len(harvest_times)
    for t in harvest_times:
        total_time += t


def format_template_numbers(x):
    if x is not None:
        return int(round(x))
    else:
        return None


def safe_list_sum(arr):
    return sum([x for x in arr if x is not None])


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


