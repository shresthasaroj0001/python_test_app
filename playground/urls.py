from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.say_hello),
    path('test-mail/', views.test_mail),
    path('test_logging/', views.test_logging)
]