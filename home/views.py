from django.shortcuts import render, redirect
import pyrebase
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

firebaseConfig = {
<<<<<<< HEAD
    "apiKey": "AIzaSyAv2Fdg7D52VvYR9TK_H_0z8NiCDj6iQkU",
    "authDomain": "heutagogy-2020.firebaseapp.com",
    "databaseURL": "https://heutagogy-2020.firebaseio.com",
    "projectId": "heutagogy-2020",
    "storageBucket": "heutagogy-2020.appspot.com",
    "messagingSenderId": "772643974559",
    "appId": "1:772643974559:web:d63b880a446d8a70dea1aa",
    "measurementId": "G-X01CP2KNV6"
=======
    "apiKey": "AIzaSyAknU0Sg2mXs5l_3zayYfrHOaXc4-HsSUc",
    "authDomain": "authdemo-1bd4d.firebaseapp.com",
    "databaseURL": "https://authdemo-1bd4d.firebaseio.com",
    "projectId": "authdemo-1bd4d",
    "storageBucket": "authdemo-1bd4d.appspot.com",
    "messagingSenderId": "524283838254",
    "appId": "1:524283838254:web:d31594249f6d02afefc4bf",
    "measurementId": "G-RPCZ9J16LB"
>>>>>>> 20389c338bff247d2129c56627d324999824f0be
  }
## For firebase authentication
firebase = pyrebase.initialize_app(firebaseConfig) 
auth = firebase.auth()

## For Firestore database storage
<<<<<<< HEAD
cred = credentials.Certificate('C:\\Users\\suma shreya t v\\Downloads\\heutagogy-2020-6959a4a76c88.json')
=======
cred = credentials.Certificate('C:\\Users\\suma shreya t v\\Downloads\\authdemo-1bd4d-9906baaec900.json')
>>>>>>> 20389c338bff247d2129c56627d324999824f0be
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
        
<<<<<<< HEAD
            context = {'email': email, 'fullname': fullname, 'photo_url': photo_url}
=======
            context = {'email': email, 'fullname': fullname, 'url': photo_url}
>>>>>>> 20389c338bff247d2129c56627d324999824f0be
            return render(request, 'home/instructor_dashboard.html', context)
        except:
            print("Email already exists")

    return render(request, 'home/sign_up.html')

<<<<<<< HEAD

=======
>>>>>>> 20389c338bff247d2129c56627d324999824f0be
def instructor_dashboard(request):
    user = auth.current_user
    context = {'dashboard_active': 'active', 'user': user}
    return render(request, 'home/instructor_dashboard.html', context)

def create_new_course(request):
    context = {'course_active': 'active'}
    return render(request, 'home/create_new_course.html', context)

def platform(request):
    return render(request, 'platform/platform.html')

def studio(request):
    return render(request, 'studio/studio.html')