from django.conf.urls import url, include
from . import views
from django.urls import path

app_name = 'admins'

urlpatterns = [
    path('admin_dashboard/', views.admin_dashboard, name="admin_dashboard"),
    path('admin_signin/', views.admin_signin, name="admin_signin"),
    path('admin_signup/', views.admin_signup, name="admin_signup"),
    path('admin_signout/', views.admin_signout, name="admin_signout"),
    path('admin_students/', views.admin_students, name="admin_students"),
    path('admin_teachers/', views.admin_teachers, name="admin_teachers"),
    path('upload_students/', views.upload_students, name="upload_students"),
    path('upload_teachers/', views.upload_teachers, name="upload_teachers"),
    path('add_new_student/', views.add_new_student, name="add_new_student"),
    path('add_new_teacher/', views.add_new_teacher, name="add_new_teacher"),
]
