import msg
from datetime import datetime, timedelta

def utc_time(local_time_str, utcoffset=0):
    local = datetime.strptime(local_time_str,
                                  "%m/%d/%Y%I:%M%p")
    utc = local - timedelta(seconds=utcoffset)
    return utc

def local_time(utc_time, utcoffset=0):
    return utc_time + timedelta(seconds=utcoffset)