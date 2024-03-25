from .common import *
import mimetypes
from celery.schedules import crontab

DEBUG = True

SECRET_KEY = 'django-insecure-kpay)tw#722ok4#gb#p!#inq#=@)&%x#q=impv!ty9(@$qz=7^'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'sql_mode': 'traditional',
        },
        'NAME': 'storefront3',
        'HOST' : 'localhost',
        'USER' : 'root',
        'PASSWORD' :'root'
    }
}

mimetypes.add_type("application/javascript", ".js", True)

DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
}

CELERY_BROKER_URL = 'redis://localhost:6379/1'

#to run celery beat; 
#celery must start: celery -A storefront worker --loglevel=info --pool=solo
#celery then beat: celery -A storefront beat
CELERY_BEAT_SCHEDULE = {
    'notify_customers' : {
        'task' : 'playground.tasks.notify_customers',
        'schedule' : 5, 
        # 'schedule' : crontab(minute='*/15') run every 15mintue using crontab
        # 'schedule' : crontab(day_of_week=1, hour=7, minute=30),
        'args' : ['Hello World'],
        # 'kwargs' : {} //key value pair
    }
}
#celery dashboard
#install: pipenv install flower
#command: celery -A storefront flower
#http://localhost:5555/
#To run redis for celery, pipenv install django-redis library is not required


#docker run -d -p 6379:6379 redis
# -d run detached mode, -p port mapping

#caching
#pipenv install django-redis

