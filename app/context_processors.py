from django.contrib import admin
from django.utils.timezone import get_current_timezone
from django.utils import timezone
import datetime


OPENING_HOUR = 9
CLOSING_HOUR = 21
SCHEDULE_DATEFORMAT = "%Y-%m-%d, %I:%M %p"
SCHEDULE_DATEFORMAT_24H = "%Y-%m-%d, %H:%M"

def site_title():
    from django.contrib.admin.sites import site
    return  site.site_title


def global_context(request):
    return CONTEXT

def get_correct_today(date=None, format=SCHEDULE_DATEFORMAT):
    if date is None:
        date = timezone.localtime()  # datetime.datetime.now(tz=get_current_timezone())
    hour = max(OPENING_HOUR, date.hour)

    minute = round(date.minute/30.0) * 30
    if minute == 60:
        minute = 0
        hour += 1

    if hour > CLOSING_HOUR:
        date = date + datetime.timedelta(days=1)
        minute = 0
        hour = OPENING_HOUR

    date = datetime.datetime(date.year, date.month,
                             date.day, hour, minute, tzinfo=get_current_timezone())

    return date.strftime(format)

CONTEXT = {
        'app_id': '55aa17c02cfc41958055ed6a536863ff',
        'app_certificate': '2a15df662d744f43b794971028e9ba4a',
        'today': get_correct_today(),
        'site_title': site_title()
    }