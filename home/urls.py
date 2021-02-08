from django.conf.urls import url, include
from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'home'

urlpatterns = [
    path('', views.landing, name = 'landing'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('password_reset_email/', views.password_reset_email, name='password_reset_email'),
    path('signup/', views.signup, name='signup'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('instructor_dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('create_course/', views.create_new_course, name='create_new_course'),
    path('create_lesson/<course>/', views.create_new_lesson, name='create_new_lesson'),
    path('courses/', views.courses, name='courses'),
    path('action_course/<course>/', views.action_course, name='action_course'),
    path('platform/<course>/<lname>/<int:slide_type>/', views.platform, name='platform'),
    path('platform/edit/<name>/', views.edit, name='edit'),
    path('addquestion/<int:id>/', views.addquestion, name='addquestion'),
    path('simple_upload/', views.simple_upload, name='simple_upload'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)