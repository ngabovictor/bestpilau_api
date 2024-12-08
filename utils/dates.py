from django.utils.timezone import localtime

today_start = localtime(None).replace(hour=0, minute=0, second=0, microsecond=0)
today_end = localtime(None).replace(hour=23, minute=59, second=59, microsecond=999999)
