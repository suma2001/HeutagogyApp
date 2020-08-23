from django.conf.urls import url, include
from . import views
from django.urls import path

app_name = 'home'

urlpatterns = [
    path('', views.landing, name = 'landing'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('instructor_dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
]
