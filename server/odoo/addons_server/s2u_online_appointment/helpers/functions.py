# -*- coding: utf-8 -*-
import re


def float_to_time(value):
    if value >= 0.0:
        ivalue = int(value)
        return "%02d:%02d" % (ivalue, (value - ivalue) * 60)
    else:
        value = abs(value)
        ivalue = int(value)
        return "-%02d:%02d" % (ivalue, (value - ivalue) * 60)

def time_to_float(value):
    hour = int(value.split(':')[0])
    minute = int(value.split(':')[1])
    floats = hour + (minute / 60)
    return floats

def valid_email(email):
    if not re.match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email.rstrip()):
        return False
    return True
