from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.http import HttpResponse
import requests

import pyrebase
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

firebaseConfig = {
    "apiKey": "AIzaSyAv2Fdg7D52VvYR9TK_H_0z8NiCDj6iQkU",
    "authDomain": "heutagogy-2020.firebaseapp.com",
    "databaseURL": "https://heutagogy-2020.firebaseio.com",
    "projectId": "heutagogy-2020",
    "storageBucket": "heutagogy-2020.appspot.com",
    "messagingSenderId": "772643974559",
    "appId": "1:772643974559:web:d63b880a446d8a70dea1aa",
    "measurementId": "G-X01CP2KNV6"
  }
## For firebase authentication
firebase = pyrebase.initialize_app(firebaseConfig) 
authe = firebase.auth()

## For Firestore database storage
cred = credentials.Certificate('heutagogy-2020-6959a4a76c88.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

teachers_collection =  db.collection('Schools').document('School 1').collection('Teachers')
students_collection =  db.collection('Schools').document('School 1').collection('Students') 
courses_collection =  db.collection('Schools').document('School 1').collection('Courses')

# Create your views here.
def landing(request):
    return render(request, 'home/landing.html')

def password_reset_email(request):
    return render(request, 'home/email.html')

def signin(request):
    print(authe.current_user)
    if request.method=="POST":
        ## Get the form data
        data = request.POST.dict()
        email = data.get('emailaddress')
        password = data.get('password')
        print(email, password)
        try:
            user = authe.sign_in_with_email_and_password(email, password)
            uid = user['localId']
            results = teachers_collection.where('uid', '==', uid).get()[0].to_dict()
            if results['First_time']==True:
                authe.send_password_reset_email(email)
                teachers_collection.document(email).update({'First_time': False})
                return redirect('home:password_reset_email')
            messages.success(request, 'Successfully signed in ' + results['Name'])
            return redirect('home:instructor_dashboard')
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error = json.loads(error_json)['error']['message']
            print(error)
            if str(error) == "INVALID_PASSWORD":
                messages.warning(request, 'Invalid login credentials')
            elif str(error) == "TOO_MANY_ATTEMPTS_TRY_LATER : Access to this account has been temporarily disabled due to many failed login attempts. You can immediately restore it by resetting your password or you can try again later.":
                messages.warning(request, 'TOO_MANY_ATTEMPTS_TRY_LATER : Access to this account has been temporarily disabled due to many failed login attempts.')
            return render(request, 'home/sign_in.html')
    return render(request, 'home/sign_in.html')

def signup(request):
    if request.method=="POST":
        ## Get the form data
        data = request.POST.dict()
        fullname = data.get('fullname')
        email = data.get('emailaddress')
        password = data.get('password')
        photo_url = data.get('url')
        print(email, password)
        ## Create a new user
        try:
            user = authe.create_user_with_email_and_password(email, password)
        
            ## Get the UID of the user
            uid = user['localId']

            ## Push this user's data to the database
            doc_ref = teachers_collection.document(email)
            doc_ref.set({
                'uid': uid,
                'Name': fullname,
                'Email': email,
                'courses': [],
                'Profile': "",
                'First_time': True,
            })
            authe.sign_in_with_email_and_password(email, password)
            return redirect('home:instructor_dashboard')
        except requests.exceptions.HTTPError as e:
            error_json = e.args[1]
            error = json.loads(error_json)['error']['message']
            print(error)
            if str(error) == "EMAIL_EXISTS":
                messages.warning(request, 'Email already exists')
            elif str(error) == "WEAK_PASSWORD : Password should be at least 6 characters":
                messages.warning(request, 'Weak Password : Password should be at least 6 characters')
            return render(request, 'home/sign_up.html')
        session_id = user['idToken']
        request.session['uid'] = str(session_id)
    return render(request, 'home/sign_up.html')

def signout(request):
    auth.logout(request)
    authe.current_user=None
    messages.success(request, 'Successfully logged out !')
    return redirect('home:signin')

def instructor_dashboard(request):
    if authe.current_user!=None:
        user = authe.current_user
        uid = user['localId']
        results = teachers_collection.where('uid', '==', uid).get()[0].to_dict()
        print(results)
        if len(results['Profile'])==0:
            url = "https://www.vippng.com/png/detail/356-3563531_transparent-human-icon-png.png"
        else:
            url = results['Profile']
        context = {'email': results['Email'], 'fullname': results['Name'], 'photo_url': url, 'dashboard_active': 'active'}
        return render(request, 'home/instructor_dashboard.html', context)
    return redirect('home:signin')


def create_new_course(request):
    if authe.current_user != None:
        if request.method=="POST":
            print("POSTED")
            data = request.POST.dict()
            print(data)
            cid = data.get('courseid') 
            course_name = data.get('coursename')
            level = data.get('level')
            general_info = data.get('description')
            lessonid = data.get('lessonid')
            lessonname = data.get('lessonname')
            lessondesc = data.get('lessondesc')
            lessonurl = data.get('lessonurl')
            print("Course Id is: ",cid)
            uid = authe.current_user['localId']

            get_course = courses_collection.where('course_id', '==', cid).get()
            print(doc_ref)
            if len(get_course) == 0:
                teachers = []
                teachers.append(uid)
                get_course = doc_ref.document(cid)
                get_course.set({
                    'course_id': cid,
                    'course_name': course_name,
                    'teacher_ids': teachers,
                    'level': level,
                    'general_info' : general_info,
                })
                lesson_content = get_course.collection('Lessons').document(lessonid)
                lesson_content.set({
                    'lesson_id': lessonid,
                    'lesson_name': lessonname,
                    'description': lessondesc,
                    'image_url': lessonurl,
                })
                slide_content = lesson_content.collection('Content').document('Slide 1')
                slide_content.set({
                    'slide_id': "S1",
                    'type': "q0",
                    'questions': [{
                        'text': 'photo_url_question',
                        'answer': 'fillup_amswer'
                        }]
                })

            else:
                print("I am in ")
                teachers = doc_ref.document(cid).get().to_dict()['teacher_ids']
                teachers.append(uid)
                print(teachers)
                doc_ref.document(cid).update({'teacher_ids': teachers})

            # context = {'course_active': 'active'}
            # return HttpResponseRedirect(reverse('home:instructor_dashboard', kwargs={'course_active': 'active'}))
            return redirect('home:instructor_dashboard')
        return render(request, 'home/createnewcourse.html', {'course_active': 'active'})
    return render(request, 'home/sign_in.html')

def platform(request):
    return render(request, 'platform/platform.html')

def studio(request):
    return render(request, 'studio/studio.html')
