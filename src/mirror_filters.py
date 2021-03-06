from google.appengine.ext.webapp import template 
from datetime import datetime, timedelta
from math import modf
import config
import os

register = template.create_template_register() 

def humanround(value, threshold=0.8):
    fraction, integer = modf(value)
    if fraction > threshold:
        return integer + 1
    else :
        return integer

@register.filter
def render_game_preview(game):
    module_path = os.path.join(config.tpl_path, 'module', 'game_preview.html')
    return template.render(module_path, {'game':game})

@register.filter
def count(listobj):
    return str(len(listobj))

@register.filter
def homelink(twit_screen_name):
    return "<span class='user_pop'><a class='homelink' href='/home/%s'>%s</a></span>" % (twit_screen_name, twit_screen_name)

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

    if seconds < 0 : 
        ret["postfix"] = "ago"
    else:
        ret["postfix"] = "left"
        
    days = abs(seconds) / SEC_TO_DAY
    hours = abs(seconds) / SEC_TO_HOUR
    mins = abs(seconds) / SEC_TO_MIN
    
    if humanround(days) > 0 :
        ret["no"] = humanround(days)
        ret["unit"] = "days"
    elif humanround(hours) > 0:
        ret["no"] = humanround(hours)
        ret["unit"] = "hours"
    elif humanround(mins) > 0:
        ret["no"] = humanround(mins)
        ret["unit"] = "minutes"
    else :
        if seconds < 0:
            return "just before"
        else:
            return "now" 

    return "%(no)d %(unit)s %(postfix)s" % (ret)
    
