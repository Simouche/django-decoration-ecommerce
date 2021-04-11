from django.utils import timezone
import datetime


def current_week_range():
    date = timezone.now()
    start_week = date - timezone.timedelta(date.weekday() + 1)
    end_week = start_week + timezone.timedelta(7)
    return start_week, end_week
