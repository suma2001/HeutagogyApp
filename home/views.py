from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.http import HttpResponse
import requests

import pyrebase
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from google.cloud import storage
from firebase import firebase
import os
import datetime
import urllib
import uuid

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./heutagogy-2020-6959a4a76c88.json"
firebase = firebase.FirebaseApplication('https://heutagogy-2020.firebaseio.com')

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
    # messages.success(request, 'Successfully logged out !')
    return redirect('home:landing')

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

def courses(request):
    if authe.current_user!=None:
        user = authe.current_user
        uid = user['localId']
        
        results = teachers_collection.where('uid', '==', uid).get()[0].to_dict()
        # print(json.dumps(results['courses']))
        if len(results['Profile'])==0:
            url = "https://www.vippng.com/png/detail/356-3563531_transparent-human-icon-png.png"
        else:
            url = results['Profile']
        dic=[]
        for c in results['courses']:
            dic.append(courses_collection.where('course_id', '==', 'C' + str(c)).get()[0].to_dict()['course_name'])
            # print()
            # l=len(list(coll.get()))
            # lessons=[]
            # for i in range(l):
                # lessons.append(coll.get()[i].to_dict()['lesson_name'])
            # dic[courses_collection.where('course_id', '==', 'C'+str(c)).get()[0].to_dict()['course_name']] = {'lessons': lessons}
        # print(dic)
        context = {'email': results['Email'], 'fullname': results['Name'], 'photo_url': url, 'course_active': 'active', 'courses': dic}
        return render(request, 'home/courses.html', context)
    return redirect('home:signin')


def action_course(request, course):
    cid = courses_collection.where('course_name', '==', course).get()[0].to_dict()['course_id']
    coll = courses_collection.document(cid).collection('Lessons')
    l=len(list(coll.get()))
    lessons=[]
    for i in range(l):
        lessons.append(coll.get()[i].to_dict()['lesson_name'])
    print(lessons)
    return render(request, 'home/lessons.html', {'lessons': lessons, 'course_active': 'active', 'course': course})


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
            
            print("Course Id is: ",cid)
            uid = authe.current_user['localId']

            get_course = courses_collection.where('course_id', '==', cid).get()
            # print(doc_ref)
            if len(get_course) == 0:
                teachers = []
                teachers.append(uid)
                get_course = courses_collection.document(cid)
                get_course.set({
                    'course_id': cid,
                    'course_name': course_name,
                    'teacher_ids': teachers,
                    'level': level,
                    'general_info' : general_info,
                })
                teacher_email = teachers_collection.where('uid', '==', uid).get()[0].to_dict()['Email']
                courses = teachers_collection.document(teacher_email).get().to_dict()['courses']
                courses.append(int(str(cid)[1:]))
                teachers_collection.document(teacher_email).update({'courses': courses})
                # lesson_content = get_course.collection('Lessons').document(lessonid)
                # lesson_content.set({
                #     'lesson_id': lessonid,
                #     'lesson_name': lessonname,
                #     'description': lessondesc,
                #     'image_url': lessonurl,
                # })

            else:
                print("I am in ")
                teachers = courses_collection.document(cid).get().to_dict()['teacher_ids']
                teachers.append(uid)
                print(teachers)
                courses_collection.document(cid).update({'teacher_ids': teachers})

            # context = {'course_active': 'active'}
            # return HttpResponseRedirect(reverse('home:instructor_dashboard', kwargs={'course_active': 'active'}))
            messages.success(request, 'Course created successfully.')
            return redirect('courses')
        return render(request, 'home/createnewcourse.html', {'create_course_active': 'active'})
    return render(request, 'home/sign_in.html')

def create_new_lesson(request, course):
    if authe.current_user != None:
        if request.method=="POST":
            print("Hello I am in")
            data = request.POST.dict()
            lessonid = data.get('lessonid')
            lessonname = data.get('lessonname')
            lessondesc = data.get('description')
            lessonurl = data.get('lessonurl')
            cid = courses_collection.where('course_name', '==', course).get()[0].to_dict()['course_id']
            lesson_content = courses_collection.document(cid).collection('Lessons').document(lessonid)
            lesson_content.set({
                'lesson_id': lessonid,
                'lesson_name': lessonname,
                'description': lessondesc,
                'image_url': lessonurl,
            })
            messages.success(request, 'Lesson created successfully.')
            return redirect('home:courses')
        return render(request, 'home/createnewlesson.html', {'create_course_active': 'active', 'course': course})
    return render(request, 'home/sign_in.html') 

def platform(request, course, lname):
    contentdic={}
    cid = courses_collection.where('course_name', '==', course).get()[0].to_dict()['course_id']
    print(cid, lname, course)
    lid = courses_collection.document(cid).collection('Lessons').where('lesson_name', '==', lname).get()[0].to_dict()['lesson_id']
    lesson = courses_collection.document(cid).collection('Lessons').where('lesson_name', '==', lname).get()[0].to_dict()
    contentdic['cid'] = cid
    contentdic['lid'] = lid
    contentdic['lesson_name'] = lesson['lesson_name']
    contentdic['description'] = lesson['description']
    contentdic['course_active'] = 'active'
    contentdic['course'] = course 

    if request.method == 'POST' and request.FILES['myfile']:
        
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        print(uploaded_file_url)
        client = storage.Client()
        bucket = client.get_bucket('heutagogy-2020.appspot.com')
        imageBlob = bucket.blob("/")
        imagePath = "media\\" + uploaded_file_url[7:]
        imageBlob = bucket.blob("QuizImages/" + uploaded_file_url[7:])
        imageBlob.upload_from_filename(imagePath)

        URL = imageBlob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
        # URL = "https://firebasestorage.googleapis.com/v0/b/" + "heutagogy-2020.appspot.com" + "/o/" + urllib.parse.quote('QuizImages/' + uploaded_file_url[7:]) + "?alt=media&token=" + uuid.uuid4().hex
        print(URL)
        quiz = []
        data = request.POST.dict()
        print(data)
        question = data.get('question')
        option1 = data.get('option1')
        if 'true1' in data:
            check1 = True
        else:
            check1 = False
        option2 = data.get('option2')
        if 'true2' in data:
            check2 = True
        else:
            check2 = False
        option3 = data.get('option3')
        if 'true3' in data:
            check3 = True
        else:
            check3 = False
        option4 = data.get('option4')
        if 'true4' in data:
            check4 = True
        else:
            check4 = False
        print(check4)
        description = data.get('description')
        
        quiz.append({
            'image': URL,
            'question': question,
            'options': [
                {
                'text': option1,
                'choice': check1
                },
                {
                'text': option2,
                'choice': check2
                },
                {
                'text': option3,
                'choice': check3
                },
                {
                'text': option4,
                'choice': check4
                }
            ]
        })
        print(quiz)
        print(contentdic)
        cid = contentdic['cid']
        lid = contentdic['lid']
        print(cid, lid)
        content = courses_collection.document(cid).collection('Lessons').document(lid).collection('Content')
        l = len(list(content.get()))
        content.document('S'+str(l+1)).set({
            'sid': 'S'+str(l+1),
            'subject': contentdic['course'],
            'questions': quiz,
            'description': description
        })

    
    return render(request, 'platform/platform.html',contentdic)



def addquestion(request, id):
    if request.method=="POST" and id==1:
        quiz = []
        data = request.POST.dict()
        question = data.get('question')
        option1 = data.get('option1')
        option2 = data.get('option2')
        option3 = data.get('option3')
        option4 = data.get('option4')
        description = data.get('description')
        quiz.append({
            'question': question,
            'option 1': option1,
            'option 2': option2,
            'option 3': option3,
            'option 4': option4
        })
        print(quiz)
        print(contentdic)
        cid = contentdic['cid']
        lid = contentdic['lid']
        print(cid, lid)
        content = courses_collection.document(cid).collection('Lessons').document(lid[2:]).collection('Content')
        l = len(list(content.get()))
        content.document('S'+str(l+1)).set({
            'sid': 'S'+str(l+1),
            'subject': contentdic['course'],
            'questions': quiz
        })
    # if request.method=="POST" and id==2:
    #     print(contentdic)
    #     cid = contentdic['cid']
    #     lid = contentdic['lid']
    #     print(cid, lid)
    #     content = courses_collection.document(cid).collection('Lessons').document(lid).collection('Content')
    #     l = len(list(content.get()))
    #     content.document('S'+str(l+1)).set({
    #         'sid': 'S'+str(l+1),
    #         'subject': contentdic['course'],
    #         'questions': quiz
    #     })
    #     quiz=[]
    return render(request, 'platform/platform.html',contentdic)

def simple_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        print(uploaded_file_url)
        return render(request, 'home/courses.html')
    return render(request, 'home/courses.html')

def studio(request):
    return render(request, 'studio/studio.html')