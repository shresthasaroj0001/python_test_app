from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Customer
from django.db.models import Value, F, Func    
from django.db import connection
from django.core.mail import send_mail, EmailMessage, mail_admins, BadHeaderError
from templated_mail.mail import BaseEmailMessage
import logging
import requests
from .tasks import notify_customers
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

def test_cache(request):
    key = 'httpbin_result'
    if cache.get(key) is None:
        response = requests.get('https://httpbin.org./delay/2')
        data = response.json()
        cache.set(key, data)
        # cache.set(key, data, 10 * 60) SETTING CACHE TIMEOUT
    return render(request,'hello.html', {'name': cache.get(key)})

#no need to define key
#need to wait until cache expire to see changes
# @cache_page(5 * 60)
# def test_cache2(request):
#     response = request.get('https://httpbin.org./delay/2')
#     data = response.json()
#     return render(request,'hello.html', {'name': cache.get(data)})

class HelloView(APIView):
    @method_decorator(cache_page(5 * 60))
    def get(self, request):
        response = requests.get('https://httpbin.org./delay/2')
        data = response.json()
        return render(request,'hello.html', {'name': data })
        # return render(request,'hello.html', {'name': cache.get(data)})

def test_background(request):
    notify_customers.delay('Hello')
    return render(request,'hello.html', {'name': 'Saroj'})

def test_logging(request):
    try:
        logger.info('Calling Method')
        response = requests.get('https://httpbin.org./delay/2')
        logger.info('Received the response')
    except requests.ConnectionError:
        logger.critical('httpbin is offline')
    return render(request,'hello.html', {'name': 'Saroj'})

def say_hello(request):
    
    #find the value by 0
    # try:
    #     query_set = Product.objects.get(pk=0)
    # except ObjectDoesNotExist:
    #     pass
    
    #the query is similar to where pk=0 limit 1
    #    product = Product.objects.filter(pk=0).first()

#range
    # query_set = Product.objects.filter(unit_price__range=(20,30))
    
    # case insensitive lookup
    # query_set = Product.objects.filter(title__icontains='coffee')

#year lookup simpliy  __year

    with connection.cursor() as cursor:
        # cursor.execute()
        cursor.callproc('get_customers',[1,2,'a'])
               
    query_set = Customer.objects.annotate(
        #Concat
        full_name=Func(F('first_name'), Value(' '), F('last_name'), function='CONCAT')
    )
    return render(request, 'hello.html',{'name' : 'Saroj Shrestha', 'products': list(query_set)});

#RUN command: docker run --rm -it -p 3000:80 -p 2525:25 rnwood/smtp4dev
#Dashboard in 
#localhost:3000

def test_mail(request):
    #Method 1
    # try:
    #     mail_admins('subject','message', html_message='message')
    # except BadHeaderError:
    #     pass

    #Method 2
    # try:
    #     message = EmailMessage('subject','message','from@a.com',['test@a.com'])
    #     message.attach_file('playground/static/images/review.png')
    #     message.send()
    # except BadHeaderError:
    #     pass

    #Method 3 : Send Template
    #pipenv install django-templated-mail
    try:
        message = BaseEmailMessage(
            template_name='emails/hello.html',
            context={'name':'Saroj'}        
        )
        message.attach_file('playground/static/images/review.png')
        message.send(['test1@a.com'])
    except BadHeaderError:
        pass
    return render(request,'hello.html',{'name':'Saroj'})  

#Background task scheduling
#docker run -d -p 6379:6369 redis 
#-d means detached 
#6379 of localhost to 6369 of redis
#0.0.0.0.6379->6379/tcp

#pipenv install redis