from django.conf.urls import url, include
from . import views
from django.urls import path

app_name = 'home'

urlpatterns = [
    path('', views.landing, name = 'landing'),
    path('signin/', views.signin, name='signin'),
    path('password_reset_email/', views.password_reset_email, name='password_reset_email'),
    path('signup/', views.signup, name='signup'),
    path('instructor_dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('create_course/', views.create_new_course, name='create_new_course'),
    path('platform/', views.platform, name='platform'),
    path('studio/', views.studio, name='studio'),
]
