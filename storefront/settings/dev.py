from .common import *
import mimetypes

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