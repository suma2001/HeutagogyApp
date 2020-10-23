from django.shortcuts import render, redirect
import firebase_admin
from firebase_admin import credentials, firestore 
import pyrebase
import xlrd

# Create your views here.
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

# cred = credentials.Certificate('heutagogy-2020-6959a4a76c88.json')
firebase = pyrebase.initialize_app(firebaseConfig) 
auth = firebase.auth()
db = firestore.client()

def admin_dashboard(request):
    return render(request, 'admins/admin_dashboard.html')

def admin_signin(request):
    if request.method=="POST":
        ## Get the form data
        data = request.POST.dict()
        email = data.get('emailaddress')
        password = data.get('password')
        print(email, password)
        
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            uid = user['localId']
            results = db.collections('Schools').document('School 1').collection('Admins').where('uid', '==', uid).get()[0].to_dict()
            return render(request, 'admins/admin_dashboard.html', results)   
        except:
            print("Wrong credentials")
            return render(request, 'admins/admin_sign_in.html')
    return render(request, 'admins/admin_sign_in.html')

def admin_signup(request):
    if request.method=="POST":
        ## Get the form data
        data = request.POST.dict()
        fullname = data.get('fullname')
        email = data.get('emailaddress')
        password = data.get('password')
        school = data.get('school')
        photo_url = data.get('url')
        
        ## Create a new user
        try:
            user = auth.create_user_with_email_and_password(email, password)
        
            ## Get the UID of the user
            uid = user['localId']
        
            ## Push this user's data to the database
            doc_ref = db.collection('Schools').document('School 1').collection('Admins').document(uid)
            doc_ref.set({
                'uid': uid,
                'email': email,
                'fullname': fullname,
                'school':school,
                'photo_url': photo_url,
            })
        
            context = {'email': email, 'fullname': fullname, 'photo_url': photo_url, 'school':school}
            return render(request, 'admins/admin_dashboard.html', context)
        except:
            print("Email already exists")

    return render(request, 'admins/admin_sign_up.html')

def add_new_student(request):
    if auth.current_user!=None:
        loc = ("student_list.xlsx")
        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(0)

        sheet.cell_value(0, 0)
        row_length = sheet.nrows
        for i in range(1, row_length):
            row = sheet.row_values(i)
            doc_ref = db.collection('Schools').document('School 1').collection('Students').document(row[0])
            doc_ref.set({
                'Roll No': row[0],
                'Password': row[1],
                'Name': row[2],
                'Class': row[3],
                'Profile': "",
                'First_time': True,
            })
        return redirect(request, 'admins:admin_dashboard')
    return render(request, 'admins/admin_sign_in.html')
