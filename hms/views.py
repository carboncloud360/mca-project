import datetime
import pandas as pd
import matplotlib.pyplot as plt
from .models import *
from .forms import DoctorForm
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .forms import ConfirmationForm

import seaborn as sns
sns.set_style('darkgrid')


def Home(request):
    return render(request, 'homepage.html')


def Admin_Home(request):
    dis = Search_Data.objects.all()
    pat = Patient.objects.all()
    doc = Doctor.objects.all()
    feed = Feedback.objects.all()

    d = {'dis': dis.count(), 'pat': pat.count(),
         'doc': doc.count(), 'feed': feed.count()}
    return render(request, 'admin_home.html', d)


def About(request):
    return render(request, 'about.html')


def Contact(request):
    return render(request, 'contact.html')


def Our_Doctors(request):
    return render(request, 'our_doctors.html')


def Login_User(request):
    error = ""
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        sign = ""
        if user:
            try:
                sign = Patient.objects.get(user=user)
            except:
                pass
            if sign:
                login(request, user)
                error = "pat1"
            else:
                pure = False
                try:
                    pure = Doctor.objects.get(status=1, user=user)
                except:
                    pass
                if pure:
                    login(request, user)
                    error = "pat2"
                else:
                    login(request, user)
                    error = "notmember"
        else:
            error = "not"
    d = {'error': error}
    return render(request, 'login.html', d)


def Login_admin(request):
    error = ""
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        if user is not None and user.is_staff:
            login(request, user)
            error = "pat"
        else:
            error = "not"
    d = {'error': error}
    return render(request, 'admin_login.html', d)


def Signup_User(request):
    error = ""
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        e = request.POST['email']
        p = request.POST['pwd']
        d = request.POST['dob']
        con = request.POST['contact']
        add = request.POST['add']
        type = request.POST['type']
        im = request.FILES['image']
        dat = datetime.date.today()
        user = User.objects.create_user(
            email=e, username=u, password=p, first_name=f, last_name=l)
        if type == "Patient":
            Patient.objects.create(
                user=user, contact=con, address=add, image=im, dob=d)
        else:
            Doctor.objects.create(dob=d, image=im, user=user,
                                  contact=con, address=add, status=2)
        error = "create"
    d = {'error': error}
    return render(request, 'register.html', d)


def Logout(request):
    logout(request)
    return redirect('home')


@login_required(login_url="login")
def assign_status(request, pid):
    doctor = Doctor.objects.get(id=pid)
    if doctor.status == 1:
        doctor.status = 2
        messages.success(
            request, 'Successfully withdrawn his approval')
    else:
        doctor.status = 1
        messages.success(request, 'Successfully approved')
    doctor.save()
    return redirect('view_doctor')


@login_required(login_url="login")
def User_Home(request):
    return render(request, 'patient_home.html')


@login_required(login_url="login")
def Doctor_Home(request):
    return render(request, 'doctor_home.html')


@login_required(login_url="login")
def Change_Password(request):
    user = request.user
    sign = None
    error = ""
    errorx = ""

    try:
        sign = Patient.objects.get(user=user)
        error = "pat"
    except Patient.DoesNotExist:
        pass

    if not sign:
        try:
            sign = Doctor.objects.get(user=user)
        except Doctor.DoesNotExist:
            pass

    if request.method == "POST":
        n = request.POST['pwd1']
        c = request.POST['pwd2']
        o = request.POST['pwd3']

        if c == n:
            user.set_password(n)
            user.save()
            errorx = "yes"
        else:
            errorx = "not"

    d = {'error': error, 'errorx': errorx, 'data': sign}
    return render(request, 'change_password.html', d)


def preprocess_inputs(df, scaler):
    df = df.copy()
    # This will Split df into X and y
    y = df['target'].copy()
    X = df.drop('target', axis=1).copy()
    X = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
    return X, y


def predict_heart_disease(list_data):
    csv_file = Admin_Health_CSV.objects.get(id=1)
    df = pd.read_csv(csv_file.csv_file)
# UCI Heart Disease Dataset which includes: Age, Sex, Chest Pain Type, Resting Blood Pressure, Serum Cholestoral, Fasting Blood Sugar, Resting Electrocardiographic Results, Maximum Heart Rate Achieved, Exercise Induced Angina, ST Depression Induced by Exercise Relative to Rest, The Slope of the Peak Exercise ST Segment, Number of Major Vessels Colored by Fluoroscopy, Thalassemia
    X = df[['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
            'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']]
    y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=0.8, random_state=0)
    nn_model = GradientBoostingClassifier(
        n_estimators=100, learning_rate=1.0, max_depth=1, random_state=0)
    nn_model.fit(X_train, y_train)
    pred = nn_model.predict([list_data])
    accuracy = nn_model.score(X_test, y_test) * 100
    print("Neural Network Accuracy: {:.2f}%".format(accuracy))
    print("Predicted Value is: ", format(pred))
    dataframe = str(df.head())
    return accuracy, pred


@login_required(login_url="login")
def add_doctor(request, pid=None):
    doctor = None
    if pid:
        doctor = Doctor.objects.get(id=pid)
    if request.method == "POST":
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            new_doc = form.save(commit=False)
            new_doc.status = 1
            if not pid:
                user = User.objects.create_user(
                    password=request.POST['password'], username=request.POST['username'], first_name=request.POST['first_name'], last_name=request.POST['last_name'])
                new_doc.user = user
            new_doc.save()
            return redirect('view_doctor')
    d = {"doctor": doctor}
    return render(request, 'add_doctor.html', d)


@login_required(login_url="login")
def add_heart_detail(request):
    if request.method == "POST":
        list_data = []
        value_dict = eval(str(request.POST)[12:-1])
        count = 0
        for key, value in value_dict.items():
            if count == 0:
                count = 1
                continue
            if key == "sex" and value[0].lower() == "male":
                list_data.append(0)
            elif key == "sex" and value[0].lower() == "female":
                list_data.append(1)
            else:
                list_data.append(value[0])
        accuracy, pred = predict_heart_disease(list_data)
        patient = Patient.objects.get(user=request.user)
        Search_Data.objects.create(
            patient=patient, prediction_accuracy=accuracy, result=pred[0], values_list=list_data)
        rem = int(pred[0])
        print("Result = ", rem)
        if pred[0] == 0:
            pred = "<span style='color:green'>You are healthy</span>"
        else:
            pred = "<span style='color:red'>You are Unhealthy, Need to Checkup.</span>"
        return redirect('predict_disease', str(rem), str(accuracy))
    return render(request, 'add_heart_detail.html')


@login_required(login_url="login")
def predict_disease(request, pred, accuracy):
    doctor = Doctor.objects.filter(
        address__icontains=Patient.objects.get(user=request.user).address)
    d = {'pred': pred, 'accuracy': accuracy, 'doctor': doctor}
    return render(request, 'predict_disease.html', d)


@login_required(login_url="login")
def view_search_pat(request):
    user = request.user

    try:
        # If the user is staff (admin), show all search data
        if user.is_staff:
            data = Search_Data.objects.all().order_by('-id')

        # If the user is a doctor, also show all search data
        elif Doctor.objects.filter(user=user).exists():
            data = Search_Data.objects.all().order_by('-id')

        # If the user is a patient, show only their own data
        elif Patient.objects.filter(user=user).exists():
            patient = Patient.objects.get(user=user)
            data = Search_Data.objects.filter(patient=patient).order_by('-id')

        else:
            data = Search_Data.objects.none()

    except Exception as e:
        print("Error:", str(e))
        data = Search_Data.objects.none()

    return render(request, 'view_search_pat.html', {'data': data})


@login_required(login_url="login")
def delete_doctor(request, pid):
    doc = Doctor.objects.get(id=pid)
    doc.delete()
    return redirect('view_doctor')


@login_required(login_url="login")
def delete_feedback(request, pid):
    doc = Feedback.objects.get(id=pid)
    doc.delete()
    return redirect('view_feedback')


@login_required(login_url="login")
def delete_patient(request, pid):
    doc = Patient.objects.get(id=pid)
    doc.delete()
    return redirect('view_patient')


@login_required(login_url="login")
def delete_searched(request, pid):
    doc = Search_Data.objects.get(id=pid)
    doc.delete()
    return redirect('view_search_pat')


@login_required(login_url="login")
def View_Doctor(request):
    doc = Doctor.objects.all()
    d = {'doc': doc}
    return render(request, 'view_doctor.html', d)


@login_required(login_url="login")
def View_Patient(request):
    patient = Patient.objects.all()
    d = {'patient': patient}
    return render(request, 'view_patient.html', d)


@login_required(login_url="login")
def View_Feedback(request):
    dis = Feedback.objects.all()
    d = {'dis': dis}
    return render(request, 'view_feedback.html', d)


@login_required(login_url="login")
def View_My_Detail(request):
    errorx = ""
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Patient.objects.get(user=user)
        error = "pat"
    except:
        sign = Doctor.objects.get(user=user)
    d = {'error': error, 'pro': sign}
    return render(request, 'profile_doctor.html', d)


@login_required(login_url="login")
def Edit_Doctor(request, pid):
    doc = Doctor.objects.get(id=pid)
    error = ""
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        e = request.POST['email']
        con = request.POST['contact']
        add = request.POST['add']
        cat = request.POST['type']
        try:
            im = request.FILES['image']
            doc.image = im
            doc.save()
        except:
            pass
        dat = datetime.date.today()
        doc.user.first_name = f
        doc.user.last_name = l
        doc.user.email = e
        doc.contact = con
        doc.category = cat
        doc.address = add
        doc.user.save()
        doc.save()
        error = "create"
    d = {'error': error, 'doc': doc}
    return render(request, 'edit_doctor.html', d)


@login_required(login_url="login")
def Edit_My_detail(request):
    errorx = ""
    user = User.objects.get(id=request.user.id)
    error = ""
    try:
        sign = Patient.objects.get(user=user)
        error = "pat"
    except:
        sign = Doctor.objects.get(user=user)
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        e = request.POST['email']
        con = request.POST['contact']
        add = request.POST['add']
        try:
            im = request.FILES['image']
            sign.image = im
            sign.save()
        except:
            pass
        to1 = datetime.date.today()
        sign.user.first_name = f
        sign.user.last_name = l
        sign.user.email = e
        sign.contact = con
        if error != "pat":
            cat = request.POST['type']
            sign.category = cat
            sign.save()
        sign.address = add
        sign.user.save()
        sign.save()
        errorx = "create"
    d = {'error': error, 'errorx': errorx, 'doc': sign}
    return render(request, 'edit_profile.html', d)


@login_required(login_url='login')
def sent_feedback(request):
    errorx = None
    if request.method == "POST":
        username = request.POST['uname']
        message = request.POST['msg']
        username = User.objects.get(username=username)
        Feedback.objects.create(user=username, messages=message)
        errorx = "create"
    return render(request, 'sent_feedback.html', {'errorx': errorx})


# email
SENDER_EMAIL = 'your_sender_email@example.com'  # Replace with your sending email

def send_confirmation(request):
    if request.method == 'POST':
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            subject = 'Booking Confirmation'
            from_email = SENDER_EMAIL
            to_email = [email]

            text_content = render_to_string('emails/confirmation_email.txt')
            html_content = render_to_string('emails/confirmation_email.html')

            msg = EmailMultiAlternatives(
                subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            try:
                msg.send()
                return render(request, 'emails/confirmation_sent.html', {'email': email})
            except Exception as e:
                # Handle errors!
                return render(request, 'emails/confirmation_error.html', {'error': str(e)})
    else:
        form = ConfirmationForm()
    return render(request, 'emails/confirmation_form.html', {'form': form})
# email
