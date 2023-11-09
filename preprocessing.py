from datetime import datetime

DATETIME_FORMAT = "%m/%d/%Y %H:%M:%S"


def parse_iso_datetime(str_dt):
    return datetime.fromisoformat(str_dt.replace("Z", "+00:00"))


def format_datetime(dt):
    return datetime.strftime(dt, DATETIME_FORMAT)
