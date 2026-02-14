from dateutil.parser import isoparse


def parse_jellyfin_date(date_str):
    return isoparse(date_str)