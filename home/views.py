from django.shortcuts import render, redirect
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
auth = firebase.auth()

## For Firestore database storage
cred = credentials.Certificate('heutagogy-2020-6959a4a76c88.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Create your views here.
def landing(request):
    return render(request, 'home/landing.html')

def signin(request):
    if request.method=="POST":
        ## Get the form data
        data = request.POST.dict()
        email = data.get('emailaddress')
        password = data.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            uid = user['localId']
            results = db.collection('Teachers').where('uid', '==', uid).get()[0].to_dict()
            return render(request, 'home/instructor_dashboard.html', results)   
        except:
            print("Wrong credentials")
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
        
        ## Create a new user
        try:
            user = auth.create_user_with_email_and_password(email, password)
        
            ## Get the UID of the user
            uid = user['localId']
        
            ## Push this user's data to the database
            doc_ref = db.collection('Teachers').document(uid)
            doc_ref.set({
                'uid': uid,
                'email': email,
                'fullname': fullname,
                'photo_url': photo_url,
                'courses' : ["C1", "C2", "C3", "C4"],
            })
        
            context = {'email': email, 'fullname': fullname, 'photo_url': photo_url}
            return render(request, 'home/instructor_dashboard.html', context)
        except:
            print("Email already exists")

    return render(request, 'home/sign_up.html')

def instructor_dashboard(request):
    user = auth.current_user
    context = {'dashboard_active': 'active', 'user': user}
    return render(request, 'home/instructor_dashboard.html', context)


def create_new_course(request):
    if auth.current_user != None:
        if request.method=="POST":
            print("POSTED")
            data = request.POST.dict()
            cid = data.get('courseid') 
            course_name = data.get('coursename')
            level = data.get('level')
            general_info = data.get('general_info')
            print("COurse Id is: ",cid)
            uid = auth.current_user['localId']

            doc_ref = db.collection('Courses').where('course_id', '==', cid).get()
            print(doc_ref)
            if len(doc_ref) == 0:
                teachers = []
                teachers.append(uid)
                db.collection('Courses').document(cid).set({
                    'course_id': cid,
                    'course_name': course_name,
                    'teacher_ids': teachers,
                    'levels': level,
                    'general_info' : general_info,
                    'lessons': ["L1", "L2", "L3"],
                })
            else:
                print("I am in ")
                teachers = db.collection('Courses').document(cid).get().to_dict()['teacher_ids']
                teachers.append(uid)
                print(teachers)
                db.collection('Courses').document(cid).update({'teacher_ids': teachers})

            # context = {'course_active': 'active'}
            return render(request, 'home/instructor_dashboard.html')
        return render(request, 'home/create_course.html')
    return render(request, 'home/sign_in.html')

def platform(request):
    return render(request, 'platform/platform.html')

def studio(request):
    return render(request, 'studio/studio.html')
