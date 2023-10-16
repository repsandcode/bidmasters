from django import template
from django.utils.timesince import timesince
from django.utils import timezone

register = template.Library()


@register.filter(name='time_ago')
def time_ago(value):
    now = timezone.now()
    time_difference = timesince(value, now).split(", ")[0]
    return time_difference
