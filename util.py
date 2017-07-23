import string
def format_time(time):
    """
    Formats seconds (with milliseconds) to a string
    """
    time=float(time)
    hours, secs=divmod(time, 3600)
    mins, secs=divmod(secs, 60)
    if secs%1 == 0:
        secf='{s:02.0f}s'
    else:
        secf='{s:06.3f}s'
    if hours==0:
        if mins==0:
            return secf.format(s=secs)
        else:
            return ('{m:.0f}m '+secf).format(m=mins,s=secs)
    else:
        return ('{h:.0f}h {m:02.0f}m '+secf).format(h=hours,m=mins,s=secs)

def format_time_delta(timedelta):
    """
    Formats a timedelta to a string
    """
    if timedelta.days==0:
        return format_time(timedelta.total_seconds())
    else:
        return '{}d '.format(timedelta.days)+format_time(timedelta.seconds+timedelta.microseconds)