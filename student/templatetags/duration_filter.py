from django import template
import datetime

register = template.Library()

@register.filter
def format_duration(duration):
    if isinstance(duration, datetime.timedelta):
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return duration