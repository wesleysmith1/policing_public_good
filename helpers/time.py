import time
import os
import math
from decimal import *
from random import randrange
getcontext().prec = 17

import logging
log = logging.getLogger(__name__)


def write_session_dir(session_identifier):
    path = f'data/session_{session_identifier}/'

    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except OSError:
            log.error("Creation of the directory %s failed" % path)
            path = 'data/'
        else:
            log.info("Successfully created the directory %s " % path)

    return path


class TimeFormatter:
    """This class accepts seconds and returns MM:SS.ss since first event"""
    def __init__(self, start):
        self.start = start

    def format(self, time):
        t = time - self.start
        minutes = math.floor(t // 60)
        seconds = t % 60
        return "{}:{}".format(minutes, seconds)
