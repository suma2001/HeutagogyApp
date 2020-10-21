from django.shortcuts import render, redirect
import firebase_admin
from firebase_admin import credentials, firestore 

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

db = firestore.client()

def admin_dashboard(request):
    return render(request, 'admins/admin_dashboard.html')

def add_new_student(request):
    
    if request.method=="POST":
        data = request.POST.dict()
        print(data)
        rollno = data.get('rollno') 
        password = data.get('password')
        name = data.get('name')
        std = data.get('std')

        doc_ref = db.collection('Students').document(rollno)
        doc_ref.set({
            'Roll No': rollno,
            'Password': password,
            'Name': name,
            'Class': std,
            'Profile': "",
            'First_time': True,
        })
        return redirect('admins:admin_dashboard')
    return render(request, "admins/add_student.html")
