from google.appengine.ext.webapp import template 
from datetime import datetime, timedelta
register = template.create_template_register() 

@register.filter 
def humantime(value): 
    return str(value) 