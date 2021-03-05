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
import random
import cloudinary
cloudinary.config(cloud_name='dc65gx08vn',
                  api_key='146415836349429',
                  api_secret='HlYXd6nOu7KkJwdrWHuNMjJClCs')
contentdic={}
contentdic['number'] = range(1,2)

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

def forgot_password(request):
    if request.method=="POST":
        email = request.POST['email']
        authe.send_password_reset_email(email)
        return redirect('home:password_reset_email')
    return render(request, 'home/forgot_password.html')

def signin(request):
    print(authe.current_user)
    if request.method=="POST":
        ## Get the form data
        data = request.POST.dict()
        email = data.get('emailaddress')
        password = data.get('password')
        if data.get('remember_me')=="false":
            request.session.set_expiry(0)
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
            return redirect('home:signin')
    return render(request, 'home/sign_in.html')

def signup(request):
    if request.method=="POST":
        ## Get the form data
        data = request.POST.dict()
        print(data)
        fullname = data.get('fullname')
        email = data.get('emailaddress')
        password = data.get('password')
        photo_url = data.get('url')
        print(email, password)
        ## Create a new user
        try:
            user = authe.create_user_with_email_and_password(email, password)
            # authe.send_email_verification(user['localId'])
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
        print(results['courses'])
        # print(json.dumps(results['courses']))
        if len(results['Profile'])==0:
            url = "https://www.vippng.com/png/detail/356-3563531_transparent-human-icon-png.png"
        else:
            url = results['Profile']
        dic=[]
        for c in results['courses']:
            dic.append(('C' + str(c), courses_collection.where('course_id', '==', 'C' + str(c)).get()[0].to_dict()['course_name']))
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


def action_course(request, cid):
    print("WOADSFGHJKMNB VCX : ", cid)
    cname = courses_collection.document(cid).get().to_dict()['course_name']
    coll = courses_collection.document(cid).collection('Lessons')
    l=len(list(coll.get()))
    lessons=[]
    for i in range(l):
        lessons.append((coll.get()[i].to_dict()['lesson_id'], coll.get()[i].to_dict()['lesson_name']))
    print(lessons)
    return render(request, 'home/lessons.html', {'lessons': lessons, 'course_active': 'active', 'course': cname, 'cid': cid})


def create_new_course(request):
    if authe.current_user != None:
        if request.method=="POST":
            print("POSTED")
            data = request.POST.dict()
            print(data)
            cid = data.get('courseid') 
            course_name = data.get('coursename')
            level = data.get('courselevel')
            print(level, type(level))
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
                    'level': int(level),
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
            return redirect('home:courses')
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


def platform(request, cid, lid, slide_type=0):
    print(slide_type, cid, lid)
    cname = courses_collection.document(cid).get().to_dict()['course_name']
    print(cid, lid)
    # lid = courses_collection.document(cid).collection('Lessons').where('lesson_name', '==', lname).get()[0].to_dict()['lesson_id']
    lesson = courses_collection.document(cid).collection('Lessons').where('lesson_id', '==', lid).get()[0].to_dict()
    print("LESSON is: ", lesson)
    contentdic['cid'] = cid
    contentdic['lid'] = lid
    contentdic['lesson_name'] = lesson['lesson_name']
    contentdic['description'] = lesson['description']
    contentdic['course_active'] = 'active'
    contentdic['course'] = cname
    # print(lesson)
    slide_contents = courses_collection.document(cid).collection('Lessons').document(lid).collection('Content')
    # print(len(slide_contents.get()))
    contentdic['slides']=[]
    i=1
    for content in slide_contents.get():
        slide_dict=content.to_dict()
        # print(slide_dict)
        s_d={}
        s_d['id']=str(i)
        i+=1
        s_d['name']=slide_dict['name']
        s_d['type']=slide_dict['type']
        s_d['description']=slide_dict['description']
        contentdic['slides'].append(s_d)
    # print(contentdic['slides'])
    fs = FileSystemStorage()
    client = storage.Client()
    bucket = client.get_bucket('heutagogy-2020.appspot.com')
    imageBlob = bucket.blob("/")    

    if request.method=='POST' and slide_type==11:
        print("ertyukjbc")
        number = request.POST['number']
        print(number)
        contentdic['number'] = range(1, int(number)+1)
        # messages.success(request, "Number of questions added.")
        return render(request, 'platform/platform.html',contentdic)
        
    ## Slide Type q7 : Fill in the missing values
    if request.method=='POST' and slide_type==8:
        print("HIIIIIIIIIIIIIIII")
        
        data = request.POST.dict()
        name = data.get('title')
        description = data.get('description')
        start = int(data.get('start'))
        end = int(data.get('end'))
        missinglist = data.get('missinglist')
        missinglist = missinglist.split(', ')   
        missingList = []
        for i in missinglist:
            missingList.append(int(i))

        l = len(list(slide_contents.get()))
        contents = slide_contents.document(lid+'S'+str(l+1))
        contents.set({
            'name': name,
            'sid': lid+'S'+str(l+1),
            'subject': contentdic['course'],
            'type': "q7",
            'description': description,
            'start': start,
            'end': end,
            'missingList': missingList
            
        })
        return render(request, 'platform/platform.html',contentdic)

    ## Slide Type q9 : Drag Drop Order
    if request.method=='POST' and slide_type==10:
        print("HIIIIIIIIIIIIIIII")
        
        data = request.POST.dict()
        name = data.get('title')
        description = data.get('description')
        
        # print(str(contentdic['number'])[9])
        num = int(str(contentdic['number'])[9])   
        questions=[]
        for i in range(1, num):
            question = data.get('question' + str(i))
            split_question = question.split(' ')
            questions.append({'question': split_question})

        l = len(list(slide_contents.get()))
        contents = slide_contents.document(lid+'S'+str(l+1))
        contents.set({
            'name': name,
            'sid': lid+'S'+str(l+1),
            'subject': contentdic['course'],
            'type': "q9",
            'description': description,
            'questions': questions,
            'numques': num-1
            
        })
        return render(request, 'platform/platform.html',contentdic)

    ## Slide Type q8 : Drag Drop Multiple
    if request.method=='POST' and slide_type==9:
        print("HIIIIIIIIIIIIIIII")
        
        data = request.POST.dict()
        name = data.get('title')
        description = data.get('description')
        category = data.get('category')
        category = category.split(', ')
        print(str(contentdic['number'])[9])
        num = int(str(contentdic['number'])[9])   
        questions=[]
        for i in range(1, num):
            name = data.get('name' + str(i))
            cate = data.get('category' + str(i))
            questions.append({
                    'first': cate,
                    'second': name
                })

        l = len(list(slide_contents.get()))
        contents = slide_contents.document(lid+'S'+str(l+1))
        contents.set({
            'name': name,
            'sid': lid+'S'+str(l+1),
            'subject': contentdic['course'],
            'type': "q8",
            'description': description,
            'questions': questions,
            'categories': category
            
        })
        return render(request, 'platform/platform.html',contentdic)

    ## Slide Type l0 : Tutorial
    if request.method=="POST" and slide_type==0:
        data = request.POST.dict()
        name = data.get('title')
        description = data.get('description')
        text_content = data.get('content')
        youtubeUrl =  data.get('url')
        video_url = ""
        files = request.FILES.dict()
        if not youtubeUrl and 'video_file' in files:
            video_file = request.FILES['video_file']
            url = cloudinary.uploader.upload(video_file, resource_type="auto", folder="SlideVideos/")
            video_url = url['secure_url']
            # filename = fs.save(video_file.name, video_file)
            # uploaded_file_url = fs.url(filename)
            print(video_url)
            # videoPath = "media\\" + uploaded_file_url[7:]
            # imageBlob = bucket.blob("SlideVideos/" + uploaded_file_url[7:])
            # imageBlob.upload_from_filename(videoPath)
            # imageBlob.make_public()
            # video_url = imageBlob.public_url

        l = len(list(slide_contents.get()))
        slide_contents.document(lid+'S'+str(l+1)).set({
            'name': name,
            'sid': lid+'S'+str(l+1),
            'subject': contentdic['course'],
            'type': "l0",
            'description': description,
            'content': text_content,
            'videoURL': video_url if video_url else youtubeUrl 
        })
        return render(request, 'platform/platform.html',contentdic)

    ## Slide Type q0 : Fill in the blanks (Images)
    if request.method=="POST" and slide_type==1:
        data = request.POST.dict()
        name = data.get('title')
        description = data.get('description')
        
        image_url = ""
        files = request.FILES.dict()
        # print(str(contentdic['number'])[9])
        num = int(str(contentdic['number'])[9])
        # num=2
        pictures=[]
        for i in range(1, num):
            answer = data.get('answer' + str(i))
            image_file = request.FILES['image_file' + str(i)]
            url = cloudinary.uploader.upload(image_file, folder="SlideImages/")
            image_url = url['secure_url']
            print(image_url)
            # filename = fs.save(image_file.name, image_file)
            # uploaded_file_url = fs.url(filename)
            # imagePath = "media\\" + uploaded_file_url[7:]
            # imageBlob = bucket.blob("SlideImages/" + uploaded_file_url[7:])
            # imageBlob.upload_from_filename(imagePath)
            # imageBlob.make_public()
            
            pictures.append({
                'correct_text': answer,
                'picture': image_url
            })

        l = len(list(slide_contents.get()))
        slide_contents.document(lid+'S'+str(l+1)).set({
            'name': name,
            'sid': lid+'S'+str(l+1),
            'subject': contentdic['course'],
            'type': "q0",
            'description': description,
            'pictures': pictures
            
        })
        return render(request, 'platform/platform.html',contentdic)
  
    ## Slide Type q6 : Fill in the blanks (Text)
    if request.method=="POST" and slide_type==7:
        data = request.POST.dict()
        name = data.get('title')
        description = data.get('description')
        
        print(str(contentdic['number'])[9])
        num = int(str(contentdic['number'])[9])   
        questions=[]
        for i in range(1, num):
            question = data.get('question' + str(i))
            answer = data.get('answer' + str(i))
            questions.append({
                'question': question,
                'correct_text': answer
            })

        l = len(list(slide_contents.get()))
        contents = slide_contents.document(lid+'S'+str(l+1))
        contents.set({
            'name': name,
            'sid': lid+'S'+str(l+1),
            'subject': contentdic['course'],
            'type': "q6",
            'description': description,
            'questions': questions
            
        })
        return render(request, 'platform/platform.html',contentdic)

    ## Slide Type q1 : MCQs (Image as options)
    if request.method=="POST" and slide_type==2:
        print("IN Image mCQs:")
        data = request.POST.dict()
        print()
        print()
        print(data)
        name = data.get('title')
        description = data.get('description')
        print(str(contentdic['number'])[9])
        num = int(str(contentdic['number'])[9])
        questions=[]
        for i in range(1, num):
            ques={}
            question = data.get('question' + str(i))
            print(question)
            if 'true'+str(i)+'1' in data:
                check1 = True
            else:
                check1 = False
            
            if 'true'+str(i)+'2' in data:
                check2 = True
            else:
                check2 = False
            
            if 'true'+str(i)+'3' in data:
                check3 = True
            else:
                check3 = False
            
            if 'true'+str(i)+'4' in data:
                check4 = True
            else:
                check4 = False

            URL=['']*4
            print(request.FILES.dict())
            for j in range(1, 5):
                # filename = fs.save(request.FILES['option' + str(i) + str(j) + '_image'].name, request.FILES['option' + str(i) + str(j) + '_image'])
                url = cloudinary.uploader.upload(request.FILES['option' + str(i) + str(j) + '_image'], folder="SlideImages/")
                # print(url)
                image_url = url['secure_url']
                print(image_url)
                # uploaded_file_url = fs.url(filename)
                # imagePath = "media\\" + uploaded_file_url[7:]
                # imageBlob = bucket.blob("SlideImages/" + uploaded_file_url[7:])
                # imageBlob.upload_from_filename(imagePath)
                # imageBlob.make_public()
                # URL[j-1] = imageBlob.public_url
                URL[j-1] = image_url
            ques['question'] = question
            ques['options'] = [
                    {
                    'picture': URL[0],
                    'correct': check1,
                    'text': ""
                    },
                    {
                    'picture': URL[1],
                    'correct': check2,
                    'text': ""
                    },
                    {
                    'picture': URL[2],
                    'correct': check3,
                    'text': ""
                    },
                    {
                    'picture': URL[3],
                    'correct': check4,
                    'text': ""
                    }
                ]
            print(ques)
            questions.append(ques)
            
        l = len(list(slide_contents.get()))
        slide_contents.document(lid+'S'+str(l+1)).set({
            'name': name,
            'sid': lid+'S'+str(l+1),
            'subject': contentdic['course'],
            'questions': questions,
            'description': description,
            'type': "q1"
        })
        return render(request, 'platform/platform.html',contentdic)

    ## Slide Type q2 : MCQs (Text as options)
    if request.method=="POST" and slide_type==3:
        print("IN Text mCQs")
        data = request.POST.dict()
        name = data.get('title')
        description = data.get('description')
        print(str(contentdic['number'])[9])
        num = int(str(contentdic['number'])[9])
        questions=[]

        for i in range(1, num):
            question = data.get('question'+str(i))
            option1 = data.get('option'+str(i)+'1')
            option2 = data.get('option'+str(i)+'2')
            option3 = data.get('option'+str(i)+'3')
            option4 = data.get('option'+str(i)+'4')

            if 'true'+str(i)+'1' in data:
                check1 = True
            else:
                check1 = False
            
            if 'true'+str(i)+'2' in data:
                check2 = True
            else:
                check2 = False
            
            if 'true'+str(i)+'3' in data:
                check3 = True
            else:
                check3 = False
            
            if 'true'+str(i)+'4' in data:
                check4 = True
            else:
                check4 = False
            questions.append({
                'text': question,
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

        l = len(list(slide_contents.get()))
        slide_contents.document(lid+'S'+str(l+1)).set({
            'name': name,
            'sid': lid+'S'+str(l+1),
            'subject': contentdic['course'],
            'questions': questions,
            'description': description,
            'type': "q2"
        })
        return render(request, 'platform/platform.html',contentdic)

    ## Slide Type q3 : Drag Drop Images
    if request.method=="POST" and slide_type==4:
        data = request.POST.dict()
        name = data.get('title')
        description = data.get('description')

        print(str(contentdic['number'])[9])
        num = int(str(contentdic['number'])[9])
        pictures=[]

        for i in range(1, num):
            answer = data.get('answer'+str(i))
            image_file = request.FILES['image_file' + str(i)]
            url = cloudinary.uploader.upload(image_file, folder="SlideImages/")
            image_url = url['secure_url']
            print(image_url)
            # filename = fs.save(image_file.name, image_file)
            # uploaded_file_url = fs.url(filename)
            # imagePath = "media\\" + uploaded_file_url[7:]
            # imageBlob = bucket.blob("SlideImages/" + uploaded_file_url[7:])
            # imageBlob.upload_from_filename(imagePath)
            # imageBlob.make_public()
            # image_url = imageBlob.public_url

            pictures.append({
                'description': answer,
                'picture': image_url
            })

        l = len(list(slide_contents.get()))
        slide_contents.document(lid+'S'+str(l+1)).set({
            'name': name,
            'sid': lid+'S'+str(l+1),
            'subject': contentdic['course'],
            'pictures': pictures,
            'description': description,
            'type': "q3"
        })

    ## Slide Type q4 : Drag Drop Audios
    if request.method=="POST" and slide_type==5:
        data = request.POST.dict()
        name = data.get('title')
        description = data.get('description')

        print(str(contentdic['number'])[9])
        num = int(str(contentdic['number'])[9])
        audios=[]

        for i in range(1, num):
            answer = data.get('answer'+str(i))
            if 'audio_file' in request.FILES.dict(): 
                audio_file = request.FILES['audio_file' + str(i)]
            url = cloudinary.uploader.upload(request.FILES['audio_file' + str(i)], resource_type = "auto", folder="SlideAudios/")
            audio_url = url['secure_url']
            print(audio_url)
            # filename = fs.save(audio_file.name, audio_file)
            # uploaded_file_url = fs.url(filename)
            # imagePath = "media\\" + uploaded_file_url[7:]
            # imageBlob = bucket.blob("SlideAudios/" + uploaded_file_url[7:])
            # imageBlob.upload_from_filename(imagePath)
            # imageBlob.make_public()
            # audio_url = imageBlob.public_url

            audios.append({
                'description': answer,
                'audio': audio_url
            })

        l = len(list(slide_contents.get()))
        slide_contents.document(lid+'S'+str(l+1)).set({
            'name': name,
            'sid': lid+'S'+str(l+1),
            'subject': contentdic['course'],
            'audios': audios,
            'description': description,
            'type': "q3"
        })

    ## Slide Type q5 : Drag Drop Text
    if request.method=="POST" and slide_type==6:
        data = request.POST.dict()
        name = data.get('title')
        description = data.get('description')

        print(str(contentdic['number'])[9])
        num = int(str(contentdic['number'])[9])
        questions=[]

        for i in range(1, num):
            text1 = data.get('text'+str(i)+'1')
            text2 = data.get('text'+str(i)+'2')
            questions.append({
                'first': text1,
                'second': text2
            })

        l = len(list(slide_contents.get()))
        slide_contents.document(lid+'S'+str(l+1)).set({
            'name': name,
            'sid': lid+'S'+str(l+1),
            'subject': contentdic['course'],
            'questions': questions,
            'description': description,
            'type': "q5"
        })
        slide_type=0
    return render(request, 'platform/platform.html', contentdic)

    

def edit(request, name):
    # cid = contentdic['cid']
    # lid = contentdic['lid']
    
    slide_content= courses_collection.document('C8').collection('Lessons').document('C8L1').collection('Content').where('name', '==', name).get()[0].to_dict()
    print("Hi ", name)
    print(slide_content)
    contentdic['slide'] = slide_content
    print(json.dumps(contentdic,sort_keys=True, indent=4))
    return render(request, 'platform/platform.html', contentdic)

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
