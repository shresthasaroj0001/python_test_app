from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.say_hello),
    path('test-mail/', views.test_mail),
    path('test_logging/', views.test_logging),
    path('test_cache/', views.test_cache),
    path('test_cache2/', views.HelloView.as_view()),
    path('test_background/', views.test_background)
    #celery -A storefront worker --loglevel=info --pool=solo //added --pool=solo because found some issues
]