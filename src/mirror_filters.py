from google.appengine.ext.webapp import template 
from datetime import datetime, timedelta
register = template.create_template_register() 

@register.filter 
def humantime(value):  
    # FIXME: not completed   
    d = value - datetime.utcnow()
    if d.days > 1 :
        return "about %d days left" % d.days
    elif d.days == 1 :
        return "about %d hours left" % (24 + d.seconds / (60 * 60))
    else:
        return "%d hours left" % (d.seconds / (60 * 60))

    return d
