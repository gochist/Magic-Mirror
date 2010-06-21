from google.appengine.ext.webapp import template 
from datetime import datetime, timedelta
register = template.create_template_register() 

@register.filter 
def humantime(value):  
    # FIXME: not completed
    SEC_TO_MIN = 60.0
    MIN_TO_HOUR = 60.0
    HOUR_TO_DAY = 24.0
    SEC_TO_HOUR = SEC_TO_MIN * MIN_TO_HOUR
    SEC_TO_DAY = SEC_TO_HOUR * HOUR_TO_DAY
       
    d = value - datetime.utcnow()
    seconds = d.days * SEC_TO_DAY + d.seconds
    ret = {}
    
#    return d#str(seconds)

    if seconds < 0 : 
        ret["postfix"] = "ago"
    else:
        ret["postfix"] = "left"
        
    days = abs(seconds) / SEC_TO_DAY
    hours = abs(seconds) / SEC_TO_HOUR
    mins = abs(seconds) / SEC_TO_MIN
    
    if round(days) > 0 :
        ret["no"] = round(days)
        ret["unit"] = "days"
    elif round(hours) > 0:
        ret["no"] = round(hours)
        ret["unit"] = "hours"
    elif round(mins) > 0:
        ret["no"] = round(mins)
        ret["unit"] = "minutes"
    else :
        if seconds < 0:
            return "just before"
        else:
            return "now" 

    return "%(no)d %(unit)s %(postfix)s" % (ret)
    
