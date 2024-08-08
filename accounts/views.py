from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.views.generic.base import TemplateView
import pyrebase
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
import firebase_admin
from firebase_admin import auth
from django.http import JsonResponse



config = {
    'apiKey': 'AIzaSyBeBvJvQm9o9tOtzCoMPcs2UeJvnrbO-yM',
    'authDomain': 'gou-adm.firebaseapp.com',
    "databaseURL": 'firebase-adminsdk-3hxpk@gou-adm.iam.gserviceaccount.com',
    'projectId': 'gou-adm',
    'storageBucket': 'gou-adm.appspot.com',
    'messagingSenderId': '909645328534',
    'appId': '1:909645328534:web:ef4322959f52e7a99452b7',
    'measurementId': 'G-1N1SH62VZV',
}
firebase= pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()



def login_view(request):
    if request.method == 'POST':
        auth = firebase.auth()
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session_id = user['idToken']
            request.session['uid'] = str(session_id)
            return render(request, 'accounts/superadmin.html')
        except Exception as e:
            print(e)  # Imprime la excepción
            message = "Invalid credentials"
            return render(request, 'accounts/login.html', {"message": message})


def config(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        
        user = authe.sign_in_with_email_and_password(email, password)

        
        user = authe.update_email(user['idToken'], email)
        user = authe.update_password(user['idToken'], password)

        
        return HttpResponseRedirect('accounts/superadmin.html')

  
    return render(request, 'accounts/config.html')
    
def usuario(request):
    if firebase_admin._apps:
        firebase_admin.delete_app(firebase_admin.get_app())
    cred = firebase_admin.credentials.Certificate('gouv2-b5056-firebase-adminsdk-mrmlq-9a19da43b2.json')
    firebase_admin.initialize_app(cred)

    users = auth.list_users().iterate_all()
    user_list = [{'uid': user.uid, 'email': user.email, 'disabled': user.disabled} for user in users]

    return render(request, 'accounts/usuario.html', {'user_list': user_list})


def crear_administrador(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            authe.create_user_with_email_and_password(email, password)
            database.child('administradores').push({'email': email})
            messages.success(request, '¡Administrador creado exitosamente!')
        except Exception as e:
            messages.error(request, 'Error al crear administrador: {}'.format(str(e)))

    return render(request, 'accounts/cuentas.html')


def logout_view(request):
    try:
        del request.session['uid']
    except KeyError:
        pass
    return render(request, 'accounts/login.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('nombre_de_la_pagina_principal')  # Reemplaza 'nombre_de_la_pagina_principal' con la URL a la que redirigir después del registro
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def eliminar_usuario(request, uid):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        if uid:
            try:
                auth.delete_user(uid)
                messages.success(request, 'El usuario se eliminó correctamente.')
            except auth.AuthError as e:
                messages.error(request, f'Ocurrió un error al eliminar el usuario: {e.error_info}')
            except Exception as e:
                messages.error(request, 'Ocurrió un error inesperado al eliminar el usuario.')
    return redirect('usuario')

def bloquear_usuario(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        if uid:
            try:
                auth.update_user(uid, disabled=True)
                messages.success(request, 'El usuario se bloqueó correctamente.')
            except auth.AuthError as e:
                messages.error(request, f'Ocurrió un error al bloquear el usuario: {e.error_info}')
            except Exception as e:
                messages.error(request, 'Ocurrió un error inesperado al bloquear el usuario.')

    return redirect('usuario')




def cuentas(request):
    if firebase_admin._apps:
        firebase_admin.delete_app(firebase_admin.get_app())
    cred = firebase_admin.credentials.Certificate('gou-adm-firebase-adminsdk-3hxpk-c216f44ec9.json')
    firebase_admin.initialize_app(cred)

    users = auth.list_users().iterate_all()
    user_list = [{'uid': user.uid, 'email': user.email, 'disabled': user.disabled} for user in users]

    return render(request, 'accounts/cuentas.html', {'user_list': user_list})

def eliminar_admin(request, uid):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        if uid:
            try:
                auth.delete_user(uid)
                messages.success(request, 'El usuario se eliminó correctamente.')
            except auth.AuthError as e:
                messages.error(request, f'Ocurrió un error al eliminar el usuario: {e.error_info}')
            except Exception as e:
                messages.error(request, 'Ocurrió un error inesperado al eliminar el usuario.')
    return redirect('cuentas')

def bloquear_admin(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        if uid:
            try:
                auth.update_user(uid, disabled=True)
                messages.success(request, 'El usuario se bloqueó correctamente.')
            except auth.AuthError as e:
                messages.error(request, f'Ocurrió un error al bloquear el usuario: {e.error_info}')
            except Exception as e:
                messages.error(request, 'Ocurrió un error inesperado al bloquear el usuario.')
    return redirect('cuentas')



from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render

@csrf_protect
def send_email(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        message = f"De: {name}\nEmail: {email}\nMensaje: {message}"

        send_mail(
            subject,
            message,
            email,
            ['gou2udec@gmail.com'],
        )

        return HttpResponse('Correo enviado')
    else:
        return render(request, 'contact.html')





class HomePageView(TemplateView):
    template_name = 'accounts/index.html'

class AboutPageView(TemplateView):
    template_name = 'accounts/about.html'

class descargaPageView(TemplateView):
    template_name = 'accounts/descarga.html'

class ContactPageView(TemplateView):
    template_name = 'accounts/contact.html'

class LoginPageView(TemplateView):
    template_name = 'accounts/login.html'
    
class superadminPageView(TemplateView):
    template_name = 'accounts/superadmin.html'

class recu_contraPageView(TemplateView):
    template_name = 'accounts/recu_contra.html'


