from datetime import datetime as dt
from datetime import timedelta


def get_date_range(sdate: str, edate: str):
    sdate = dt.strptime(sdate, "%m/%d/%Y")
    edate = dt.strptime(edate, "%m/%d/%Y")
    return [(sdate + timedelta(days=x)).date()
            for x in range((edate - sdate).days)]
