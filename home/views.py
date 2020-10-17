from django.shortcuts import render

# Create your views here.
def landing(request):
    return render(request, 'home/landing.html')

def signin(request):
    return render(request, 'home/sign_in.html')

def signup(request):
    return render(request, 'home/sign_up.html')

def instructor_dashboard(request):
    context = {'dashboard_active': 'active'}
    return render(request, 'home/instructor_dashboard.html', context)

def create_new_course(request):
    context = {'course_active': 'active'}
    return render(request, 'home/create_new_course.html', context)