from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
import firebase_admin
from firebase_admin import auth, credentials, delete_app
from firebase_admin.exceptions import NotFoundError, FirebaseError
from pymongo import MongoClient
from .firebase_config import auth, database, firebase
from .models import Usuario



from firebase_admin import auth, exceptions
from pymongo import MongoClient
from django.contrib import messages
from django.shortcuts import redirect





'''.........................................................vistas generales...........................................................'''

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

# Envía un correo electrónico con los detalles del contacto.
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



'''...............................................vistas específicas........................................................................'''

 # Mostrar fotografía de los administradores   
def perfil_usuario(request):
    client = MongoClient('mongodb+srv://GoU:gou22024@clustergou.0rlnvqb.mongodb.net/GoU?retryWrites=true&w=majority')
    db = client['Gou']
    collection = db['GoUadmin']
 
    usuario = collection.find_one({'correo': request.user.email})
    
    if usuario and 'foto' in usuario:
        image_data = usuario['foto']
    else:
        image_data = 'accounts/static/img/avatar5.png' # Puede ser una imagen predeterminada o None si no existe la foto

    return render(request, 'accounts/perfil_usuario.html', {
        'image_data': image_data
    })


# Muestra la lista de administradores (Bloqueados y sin bloquear).
def cuentas(request):
    client = MongoClient('mongodb+srv://GoU:gou22024@clustergou.0rlnvqb.mongodb.net/GoU?retryWrites=true&w=majority')
    db = client['Gou']
    collection = db['GoUadmin']

    try:
        all_users = collection.find()
        users_blocked = [
            {
                'id': str(user.get('_id')),  
                'nombre': user.get('nombre'),
                'apellido': user.get('apellido'),
                'rol': user.get('rol'),
                'email': user.get('correo')
            }
            for user in all_users if user.get('bloqueado') == True
        ]

        users = collection.find({'bloqueado': {'$ne': True}})
        user_list = [
            {
                'id': str(user.get('_id')),  
                'nombre': user.get('nombre'),
                'apellido': user.get('apellido'),
                'rol': user.get('rol'),
                'email': user.get('correo')
            }
            for user in users
        ]

        # Renderizar la plantilla y pasar las listas de usuarios
        return render(request, 'accounts/cuentas.html', {'users_blocked': users_blocked, 'user_list': user_list})

    except Exception as e:
        # Manejar posibles errores y mostrar un mensaje de error en la plantilla
        messages.error(request, f'Ocurrió un error al obtener la lista de usuarios: {e}')
        return render(request, 'accounts/cuentas.html', {'users_blocked': [], 'user_list': []})



# Maneja el inicio de sesión usando Firebase Authentication y verifica el usuario en MongoDB. 
def login_view(request):
    if request.method == 'POST':
        auth = firebase.auth()
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Autenticación con Firebase
            user = auth.sign_in_with_email_and_password(email, password)
            session_id = user['idToken']
            request.session['uid'] = str(session_id)

            # Conectar a MongoDB
            client = MongoClient('mongodb+srv://GoU:gou22024@clustergou.0rlnvqb.mongodb.net/GoU?retryWrites=true&w=majority')
            db = client['Gou']
            collection = db['GoUadmin']

            # Buscar el usuario en MongoDB usando el correo electrónico
            usuario = collection.find_one({'correo': email})

            if usuario:
                # Si se encuentra el usuario, renderizar la plantilla con los datos
                return render(request, 'accounts/superadmin.html', {'usuario': usuario})
            else:
                # Si no se encuentra el usuario, mostrar un mensaje de error
                message = "Usuario no encontrado en la base de datos"
                return render(request, 'accounts/login.html', {"message": message})

        except Exception as e:
            # Si ocurre un error, manejarlo y mostrar un mensaje
            print(e)
            message = "Credenciales inválidas o error en la autenticación"
            return render(request, 'accounts/login.html', {"message": message})

    return render(request, 'accounts/login.html')


# Permite actualizar el correo y la contraseña del usuario autenticado.
def config(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        
        user = authe.sign_in_with_email_and_password(email, password)

        
        user = authe.update_email(user['idToken'], email)
        user = authe.update_password(user['idToken'], password)

        
        return HttpResponseRedirect('accounts/superadmin.html')

  
    return render(request, 'accounts/config.html')


#Lista los usuarios.
def usuario(request):
    # Conectar a MongoDB
    client = MongoClient('mongodb+srv://GoU:gou22024@clustergou.0rlnvqb.mongodb.net/GoU?retryWrites=true&w=majority')
    db = client['Gou']
    
    # Seleccionar las colecciones
    usuarios_collection = db['Usuarios']
    invitados_collection = db['UsuarioInvitado']
    
    try:
        # Obtener los documentos de ambas colecciones
        usuarios = list(usuarios_collection.find({}, {'_idusuario': 1, 'nombre': 1, 'apellidos': 1, 'telefono': 1, 'email': 1, 'bloqueado': 1}))
        invitados = list(invitados_collection.find({}, {'_idusuario': 1, 'nombre': 1, 'apellidos': 1, 'telefono': 1, 'email': 1, 'bloqueado': 1}))

        # Renombrar la clave _idusuario a idusuario
        for usuario in usuarios:
            usuario['idusuario'] = usuario.pop('_idusuario')
        for invitado in invitados:
            invitado['idusuario'] = invitado.pop('_idusuario')

        # Crear listas separadas para usuarios bloqueados y no bloqueados
        usuarios_blocked = [
            {
                'idusuario': user.get('idusuario'),
                'nombre': user.get('nombre'),
                'apellidos': user.get('apellidos'),
                'telefono': user.get('telefono'),
                'email': user.get('email')
            }
            for user in usuarios if user.get('bloqueado') == True
        ]

        usuarios_not_blocked = [
            {
                'idusuario': user.get('idusuario'),
                'nombre': user.get('nombre'),
                'apellidos': user.get('apellidos'),
                'telefono': user.get('telefono'),
                'email': user.get('email')
            }
            for user in usuarios if user.get('bloqueado') != True
        ]

        invitados_blocked = [
            {
                'idusuario': guest.get('idusuario'),
                'nombre': guest.get('nombre'),
                'apellidos': guest.get('apellidos'),
                'telefono': guest.get('telefono'),
                'email': guest.get('email')
            }
            for guest in invitados if guest.get('bloqueado') == True
        ]

        invitados_not_blocked = [
            {
                'idusuario': guest.get('idusuario'),
                'nombre': guest.get('nombre'),
                'apellidos': guest.get('apellidos'),
                'telefono': guest.get('telefono'),
                'email': guest.get('email')
            }
            for guest in invitados if guest.get('bloqueado') != True
        ]

         # Combinar las listas de usuarios bloqueados e invitados bloqueados
        combined_blocked = usuarios_blocked + invitados_blocked

        # Renderizar la plantilla y pasar la lista combinada
        return render(request, 'accounts/usuario.html', {
            'combined_blocked': combined_blocked,
            'usuarios_not_blocked': usuarios_not_blocked,
            'invitados_not_blocked': invitados_not_blocked
        })

    except Exception as e:
        # Manejo de errores
        print(e)
        return render(request, 'accounts/usuario.html', {'error': str(e)})

    

# MONGO DB - Nombre de usuarios 
# Muestra la información del primer usuario en la colección de MongoDB.
client = MongoClient('mongodb+srv://GoU:gou22024@clustergou.0rlnvqb.mongodb.net/GoU?retryWrites=true&w=majority')
db = client['Gou']  # Reemplaza con el nombre de tu base de datos
usuarios_collection = db['Usuarios']

def usuario_info(request):
    # Consulta para obtener el primer usuario en la colección
    usuario = usuarios_collection.find_one()  # Modifica según el criterio de búsqueda que necesites
    nombre_usuario = usuario['nombre']  # Reemplaza 'nombre' con el campo que contiene el nombre del usuario

    return render(request, 'ruta/a/tu/superadmin.html', {'nombre_usuario': nombre_usuario})



'''..............................................gestión de usuarios y administradores....................................................................'''

def eliminar_usuario(request, email):

    if not firebase_admin._apps:
        cred = credentials.Certificate('gouv2-b5056-firebase-adminsdk-mrmlq-7abf803639.json')
        firebase_admin.initialize_app(cred)
    
    try:
        user_record = auth.get_user_by_email(email)

        auth.delete_user(user_record.uid)

        client = MongoClient('mongodb+srv://GoU:gou22024@clustergou.0rlnvqb.mongodb.net/GoU?retryWrites=true&w=majority')
        db = client['Gou']
        usuarios_collection = db['Usuarios']
        invitados_collection = db['UsuarioInvitado']

        result_usuarios = usuarios_collection.delete_one({'email': email})
        result_invitados = invitados_collection.delete_one({'email': email})

        # Verificar si el usuario fue eliminado en alguna colección
        if result_usuarios.deleted_count > 0 or result_invitados.deleted_count > 0:
            messages.success(request, 'El usuario se eliminó correctamente de Firebase y MongoDB.')
        else:
            messages.warning(request, 'El usuario fue eliminado de Firebase, pero no se encontró en MongoDB.')

    except exceptions.FirebaseError as e:
        messages.error(request, f'Ocurrió un error al interactuar con Firebase: {e}')
    except Exception as e:
        messages.error(request, f'Ocurrió un error inesperado al eliminar el usuario: {e}')

    return redirect('usuario')




def bloquear_usuario(request, email):
    # Inicializar Firebase solo si no está ya inicializado
    if not firebase_admin._apps:
        cred = credentials.Certificate('gouv2-b5056-firebase-adminsdk-mrmlq-7abf803639.json')
        firebase_admin.initialize_app(cred)

    try:
        # Obtener el usuario de Firebase
        user_record = auth.get_user_by_email(email)

        # Conectar a MongoDB
        client = MongoClient('mongodb+srv://GoU:gou22024@clustergou.0rlnvqb.mongodb.net/GoU?retryWrites=true&w=majority')
        db = client['Gou']
        usuarios_collection = db['Usuarios']
        invitados_collection = db['UsuarioInvitado']

        # Actualizar el campo 'bloqueado' a True en la colección Usuarios
        result_usuarios = usuarios_collection.update_one(
            {'email': email},
            {'$set': {'bloqueado': True}}
        )

        # Actualizar el campo 'bloqueado' a True en la colección Invitados
        result_invitados = invitados_collection.update_one(
            {'email': email},
            {'$set': {'bloqueado': True}}
        )

        # Verificar si el usuario fue bloqueado en alguna colección
        if result_usuarios.matched_count > 0 or result_invitados.matched_count > 0:
            messages.success(request, 'El usuario se bloqueó correctamente en MongoDB.')
        else:
            messages.warning(request, 'El usuario fue encontrado en Firebase, pero no se encontró en MongoDB.')

    except exceptions.FirebaseError as e:
        messages.error(request, f'Ocurrió un error al interactuar con Firebase: {e}')
    except Exception as e:
        messages.error(request, f'Ocurrió un error inesperado al bloquear el usuario: {e}')

    return redirect('usuario')



def desbloquear_usuario(request, email):
    # Inicializar Firebase solo si no está ya inicializado
    if not firebase_admin._apps:
        cred = credentials.Certificate('gouv2-b5056-firebase-adminsdk-mrmlq-7abf803639.json')
        firebase_admin.initialize_app(cred)

    try:
        # Obtener el usuario de Firebase
        user_record = auth.get_user_by_email(email)

        # Conectar a MongoDB
        client = MongoClient('mongodb+srv://GoU:gou22024@clustergou.0rlnvqb.mongodb.net/GoU?retryWrites=true&w=majority')
        db = client['Gou']
        usuarios_collection = db['Usuarios']
        invitados_collection = db['UsuarioInvitado']

        # Actualizar el campo 'bloqueado' a False en la colección Usuarios
        result_usuarios = usuarios_collection.update_one(
            {'email': email},
            {'$set': {'bloqueado': False}}
        )

        # Actualizar el campo 'bloqueado' a False en la colección Invitados
        result_invitados = invitados_collection.update_one(
            {'email': email},
            {'$set': {'bloqueado': False}}
        )

        # Verificar si el usuario fue desbloqueado en alguna colección
        if result_usuarios.matched_count > 0 or result_invitados.matched_count > 0:
            messages.success(request, 'El usuario se desbloqueó correctamente en MongoDB.')
        else:
            messages.warning(request, 'El usuario fue encontrado en Firebase, pero no se encontró en MongoDB.')

    except exceptions.FirebaseError as e:
        messages.error(request, f'Ocurrió un error al interactuar con Firebase: {e}')
    except Exception as e:
        messages.error(request, f'Ocurrió un error inesperado al desbloquear el usuario: {e}')

    return redirect('usuario')




def eliminar_admin(request, email):
    if not firebase_admin._apps:
        cred = credentials.Certificate('gou-adm-firebase-adminsdk-3hxpk-c216f44ec9.json')
        firebase_admin.initialize_app(cred)

    try:
        user_record = auth.get_user_by_email(email)
        auth.delete_user(user_record.uid)

        # Eliminar el usuario en MongoDB
        client = MongoClient('mongodb+srv://GoU:gou22024@clustergou.0rlnvqb.mongodb.net/GoU?retryWrites=true&w=majority')
        db = client['Gou']
        collection = db['GoUadmin']
        result = collection.delete_one({'correo': email})

        if result.deleted_count > 0:
            messages.success(request, 'El administrador se eliminó correctamente de Firebase y MongoDB.')
        else:
            messages.warning(request, 'El administrador fue eliminado de Firebase, pero no se encontró en MongoDB.')

    except exceptions.FirebaseError as e:
        messages.error(request, 'Ocurrió un error al interactuar con Firebase.')
    except Exception as e:
        messages.error(request, 'Ocurrió un error inesperado al eliminar el usuario.')

    return redirect('cuentas')



def bloquear_admin(request, email):
    if not firebase_admin._apps:
        cred = credentials.Certificate('gou-adm-firebase-adminsdk-3hxpk-c216f44ec9.json')
        firebase_admin.initialize_app(cred)

    try:
        # Obtener el registro del usuario por correo electrónico en Firebase
        user_record = auth.get_user_by_email(email)

        # Bloquear al usuario en Firebase (deshabilitar su cuenta)
        auth.update_user(user_record.uid, disabled=True)

        # Bloquear al usuario en MongoDB (puedes agregar un campo que indique que está bloqueado)
        client = MongoClient('mongodb+srv://GoU:gou22024@clustergou.0rlnvqb.mongodb.net/GoU?retryWrites=true&w=majority')
        db = client['Gou']
        collection = db['GoUadmin']
        result = collection.update_one({'correo': email}, {'$set': {'bloqueado': True}})

        if result.matched_count > 0:
            messages.success(request, 'El administrador se bloqueó correctamente en Firebase y MongoDB.')
        else:
            messages.warning(request, 'El administrador fue bloqueado en Firebase, pero no se encontró en MongoDB.')

    except exceptions.FirebaseError as e:
        messages.error(request, f'Ocurrió un error al interactuar con Firebase: {e}')
    except Exception as e:
        messages.error(request, f'Ocurrió un error inesperado al bloquear el usuario: {e}')

    return redirect('cuentas')


def desbloquear_admin(request, email):
    if not firebase_admin._apps:
        cred = credentials.Certificate('gou-adm-firebase-adminsdk-3hxpk-c216f44ec9.json')
        firebase_admin.initialize_app(cred)

    try:
        # Obtener el registro del usuario por correo electrónico en Firebase
        user_record = auth.get_user_by_email(email)

        # Desbloquear al usuario en Firebase (habilitar su cuenta)
        auth.update_user(user_record.uid, disabled=False)

        # Desbloquear al usuario en MongoDB (actualizar el campo de bloqueado)
        client = MongoClient('mongodb+srv://GoU:gou22024@clustergou.0rlnvqb.mongodb.net/GoU?retryWrites=true&w=majority')
        db = client['Gou']
        collection = db['GoUadmin']
        result = collection.update_one({'correo': email}, {'$set': {'bloqueado': False}})

        if result.matched_count > 0:
            messages.success(request, 'El administrador se desbloqueó correctamente en Firebase y MongoDB.')
        else:
            messages.warning(request, 'El administrador fue desbloqueado en Firebase, pero no se encontró en MongoDB.')

    except exceptions.FirebaseError as e:
        messages.error(request, f'Ocurrió un error al interactuar con Firebase: {e}')
    except Exception as e:
        messages.error(request, f'Ocurrió un error inesperado al desbloquear el administrador: {e}')

    return redirect('cuentas')



def crear_administrador(request):
    if request.method == 'POST':
    
        client = MongoClient('mongodb+srv://GoU:gou22024@clustergou.0rlnvqb.mongodb.net/GoU?retryWrites=true&w=majority')
        db = client['Gou']
        collection = db['GoUadmin']

        # Inicializa la conexión con Firebase con un nombre único
        cred = credentials.Certificate("gou-adm-firebase-adminsdk-3hxpk-c216f44ec9.json")
        app = firebase_admin.initialize_app(cred, name='admin_app')

        # Obtiene los datos del formulario
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        rol = request.POST.get('rol')
        correo = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Guarda los datos en MongoDB
            administrador = {
                'nombre': nombre,
                'apellido': apellido,
                'rol': rol,
                'correo': correo,
            }
            collection.insert_one(administrador)

            # Crea un usuario en Firebase Authentication
            user = auth.create_user(
                app=app,
                email=correo,
                password=password
            )

            messages.success(request, '¡Administrador creado exitosamente!')
        except Exception as e:
            messages.error(request, f'Error al crear administrador: {str(e)}')
        finally:
            # Elimina la app de Firebase para evitar conflictos futuros
            delete_app(app)

    return redirect('cuentas')







'''............................................................POR AGREGAR...........................................................'''








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



def superadmin_view(request):
    usuarios = Usuario.objects.all()  # Extraer todos los documentos de la colección `usuarios`
    return render(request, 'superadmin.html', {'usuarios': usuarios})













