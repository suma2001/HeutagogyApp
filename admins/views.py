from django.shortcuts import render, redirect
import firebase_admin
from firebase_admin import credentials, firestore 
import pyrebase
import xlrd
import openpyxl

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
    user = auth.current_user
    print(user)
    context = {'user': user}
    return render(request, 'admins/admin_dashboard.html', context)

def admin_signin(request):
    if request.method=="POST":
        ## Get the form data
        data = request.POST.dict()
        email = data.get('emailaddress')
        password = data.get('password')
        print(email, password, "Admins")
        
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            uid = user['localId']
            results = db.collection('Schools').document('School 1').collection('Admins').where('uid', '==', uid).get()[0].to_dict()
            # print(results)
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
            doc_ref = db.collection('Schools').document(school).collection('Admins').document(uid)
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

def admin_students(request):
    if auth.current_user!=None:
        Students = db.collection('Schools').document('School 1').collection('Students')
        students = Students.stream()
        # print(docs)
        student_list=[]
        i=1
        for doc in students:
            t = (i, doc.to_dict())
            student_list.append(t)
            i+=1
        
        return render(request, 'admins/student_list.html', {'student_list' : student_list})
    return render(request, 'admins/admin_sign_in.html')


def upload_students(request):
    if auth.current_user!=None:
        if request.method=="POST":
            excel_file = request.FILES["excel_file"]
            print(excel_file)
            # loc = ("student_list.xlsx")
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb["Sheet1"]
            print(sheet)
            
            # print(sheet.iter_rows()[0])
            for col in sheet.iter_rows():
                col_length = len(col)
                break
            print("Col length : ", col_length)

            for row in sheet.iter_cols():
                row_length = len(row)
                break
            print("Row length : ", row_length)
            
            for i in range(2, row_length+1):
                st = "A"+str(i)
                print(st)
                l=[]
                doc_ref = db.collection('Schools').document('School 1').collection('Students').document(sheet[st].value)
                doc = doc_ref.get()
                if doc.exists:
                    continue
                else:
                    for j in range(0, col_length):
                        st = chr(ord("A") + j) + str(i)
                        l.append(sheet[st].value)
                    print(l)
                    doc_ref.set({
                        'Roll_No': l[0],
                        'Password': l[1],
                        'Name': l[2],
                        'Class': l[3],
                        'Profile': "",
                        'First_time': True,
                    })
            return redirect('admins:admin_students')
        return render(request, 'admins/add_students.html')
    return render(request, 'admins/admin_sign_in.html')

def add_new_student(request):
    if auth.current_user!=None:
        if request.method=="POST":
            data = request.POST.dict()
            rollno = data.get('rollno')
            password = data.get('password')
            name = data.get('name')
            std = data.get('std')

            doc_ref = db.collection('Schools').document('School 1').collection('Students').document(rollno)
            doc_ref.set({
                'Roll_No': rollno,
                'Password': password,
                'Name': name,
                'Class': std,
                'Profile': "",
                'First_time': True,
            })
            return redirect(request, 'admins:admin_students')
        return render(request, 'admins/add_student.html')
    return render(request, 'admins/admin_sign_in.html')


def add_new_teacher(request):
    if auth.current_user!=None:
        loc = ("student_list.xlsx")
        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(1)

        sheet.cell_value(0, 0)
        row_length = sheet.nrows
        for i in range(1, row_length):
            row = sheet.row_values(i)
            email = row[1]
            password = row[2]
            print(type(password))
            teacher = auth.create_user_with_email_and_password(email, password)
            uid = teacher['localId']
            doc_ref = db.collection('Schools').document('School 1').collection('Teachers').document(row[1])
            doc_ref.set({
                'uid': uid,
                'Name': row[0],
                'Email': row[1],
                'courses': [],
                'Profile': "",
                'First_time': True,
            })
        return redirect(request, 'admins:admin_dashboard')
    return render(request, 'admins/admin_sign_in.html')
