from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.generic.base import TemplateView
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import JsonResponse
from bson import ObjectId
import firebase_admin
from firebase_admin import auth, credentials, delete_app, exceptions
from firebase_admin.exceptions import NotFoundError, FirebaseError
from pymongo import MongoClient
from .firebase_config import auth, database, firebase
from .models import Usuario
import base64
from django.shortcuts import redirect



# Inicializar la conexión de MongoDB

client = MongoClient('mongodb+srv://gouudec2024:gou22024@gouv2.fbdwx.mongodb.net/?retryWrites=true&w=majority&appName=GoUv2')
db = client['GoUV2']




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

def principal(request):
    email = request.session.get('email')
    usuario = db['GoUadmin'].find_one({'correo': email})

    if usuario:
        rol = usuario['rol']
        image_data = usuario['foto']
        return render(request, 'accounts/principal.html', {'rol': rol, 'image_data': image_data, 'usuario': usuario})
    return render(request, 'accounts/principal.html')
    

class recu_contraPageView(TemplateView):
    template_name = 'accounts/recu_contra.html'


@csrf_protect
def send_email(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_content = request.POST.get('message', '').strip()

        if not name or not email or not subject or not message_content:
            messages.error(request, 'Por favor, completa todos los campos requeridos.')
            return redirect('contact')  

        message = f"De: {name}\nEmail: {email}\nMensaje:\n\n{message_content}"

        try:
            send_mail(
                subject,                    
                message,                    
                'gou2udec@gmail.com',       
                ['gou2udec@gmail.com'],     
                fail_silently=False,        
            )
            
            messages.success(request, 'Correo enviado correctamente.')
            return redirect('contact') 
        except Exception as e:
            messages.error(request, 'Error al enviar el correo. Intenta nuevamente más tarde.')
            return redirect('contact') 
    else:
        return redirect('contact') 




'''...............................................vistas específicas........................................................................'''

# Muestra la lista de administradores (Bloqueados y sin bloquear).
def cuentas(request):
    email = request.session.get('email')
    usuario = db['GoUadmin'].find_one({'correo': email})
    if usuario:
        rol = usuario['rol']
        image_data = usuario['foto']
        if rol != 'Súper Administrador':
            messages.error(request, 'Acceso denegado: No cuenta con los permisos necesarios para visualizar esta sección.')
            return redirect('principal')

    

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

        return render(request, 'accounts/cuentas.html', {'users_blocked': users_blocked, 'user_list': user_list, 'rol': rol, 'image_data': image_data, 'usuario': usuario})
    


    except Exception as e:
        messages.error(request, f'Ocurrió un error al obtener la lista de usuarios: {e}')
        return render(request, 'accounts/cuentas.html', {'users_blocked': [], 'user_list': []})



# Maneja el inicio de sesión usando Firebase Authentication y verifica el usuario en MongoDB. 
def login_view(request):
    if request.method == 'POST':
        auth = firebase.auth()
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session_id = user['idToken']
            request.session['uid'] = str(session_id)

            request.session['email'] = email

            collection = db['GoUadmin']

            usuario = collection.find_one({'correo': email})

            if usuario:
                rol = usuario['rol']
                image_data = usuario['foto']
                return render(request, 'accounts/principal.html', {'rol': rol, 'image_data': image_data, 'usuario': usuario})
            else:
                message = "Usuario no encontrado en la base de datos"
                return render(request, 'accounts/login.html', {"message": message})

        except Exception as e:
            message = "Credenciales inválidas o error en la autenticación"
            return render(request, 'accounts/login.html', {"message": message})

    return render(request, 'accounts/login.html')


# Visualizar el apartado de configuración
def config(request):
    email = request.session.get('email')

    if not email:
        messages.error(request, 'Debe iniciar sesión primero.')
        return redirect('login')

    if request.method == 'POST':
        nombre = request.POST.get('name')
        apellido = request.POST.get('surname')
        password = request.POST.get('password')
        foto = request.FILES.get('photo')

        collection = db['GoUadmin']

        if not firebase_admin._apps:
            cred = credentials.Certificate('gou-adm-firebase-adminsdk-3hxpk-c216f44ec9.json')
            firebase_admin.initialize_app(cred)

        try:
            update_data = {}
            if nombre:
                update_data["nombre"] = nombre
            if apellido:
                update_data["apellido"] = apellido
            if foto:
                foto_base64 = base64.b64encode(foto.read()).decode('utf-8')
                update_data["foto"] = foto_base64

            if update_data:
                collection.update_one({"correo": email}, {"$set": update_data})

            if password:
                user = auth.get_user_by_email(email)
                auth.update_user(user.uid, password=password)

            messages.success(request, 'Datos actualizados exitosamente.')

        except Exception as e:
            messages.error(request, f'Error al actualizar los datos: {str(e)}')

        return redirect('login')
    
    return render(request, 'accounts/config.html')


# Visualizar los usuarios.
def usuario(request):
    usuarios_collection = db['Usuarios']
    invitados_collection = db['UsuarioInvitado']
    
    try:
        usuarios = list(usuarios_collection.find({}, {'_idusuario': 1, 'nombre': 1, 'apellidos': 1, 'telefono': 1, 'email': 1, 'bloqueado': 1}))
        invitados = list(invitados_collection.find({}, {'_idusuario': 1, 'nombre': 1, 'apellidos': 1, 'telefono': 1, 'email': 1, 'bloqueado': 1}))

        for usuario in usuarios:
            usuario['idusuario'] = usuario.pop('_idusuario')
        for invitado in invitados:
            invitado['idusuario'] = invitado.pop('_idusuario')

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
        combined_blocked = usuarios_blocked + invitados_blocked

        email = request.session.get('email')
        usuario = db['GoUadmin'].find_one({'correo': email})
        if usuario:
            rol = usuario['rol']
            image_data = usuario['foto']
            return render(request, 'accounts/usuario.html', {
                'combined_blocked': combined_blocked,
                'usuarios_not_blocked': usuarios_not_blocked,
                'invitados_not_blocked': invitados_not_blocked, 
                'rol': rol, 
                'image_data': image_data, 
                'usuario': usuario
        })

    except Exception as e:
        return render(request, 'accounts/usuario.html', {'error': str(e)})



# Visualizar los documentos
def documento(request):
    collection_registros = db['RegistrosAutos']
    collection_admin = db['GoUadmin']
    collection_politicas = db['Politi_Acuer_otros']
  
    email = request.session.get('email')
    usuario = collection_admin.find_one({'correo': email})

    registros = list(collection_registros.find({'RespuestaAprobacion': False, 'Rechazado': False}))

    for registro in registros:
        registro['idusuario'] = registro.pop('_idusuario', None)
        registro['id'] = str(registro['_id']) 

    politicas = collection_politicas.find_one({}, {'Costo_Km': 1})  
    costo_km_actual = politicas.get('Costo_Km', 0) 
    contexto = {'registros': registros, 'costo_km_actual': costo_km_actual}  

    if usuario:
        contexto.update({'rol': usuario['rol'], 'image_data': usuario['foto'], 'usuario': usuario})

    return render(request, 'accounts/documento.html', contexto)



# Visualizar las reseñas
def resena(request):
    email = request.session.get('email')
    usuario = db['GoUadmin'].find_one({'correo': email})

    collection = db['HistorialDeRutas']
    
    pipeline = [
        {
            '$match': {
                '$or': [
                    {'reservasInfo.revisada': {'$ne': True}},
                    {'cumplioRutaInfoPasajeros.revisada': {'$ne': True}}
                ]
            }
        },
        {
            '$project': {
                'reservasInfo': {
                    '$filter': {
                        'input': '$reservasInfo',
                        'as': 'reserva',
                        'cond': {'$eq': ['$$reserva.revisada', False]}
                    }
                },
                'cumplioRutaInfoPasajeros': {
                    '$filter': {
                        'input': '$cumplioRutaInfoPasajeros',
                        'as': 'pasajero',
                        'cond': {'$eq': ['$$pasajero.revisada', False]}
                    }
                }
            }
        }
    ]

    rutas = collection.aggregate(pipeline)

    contexto = {'resenas': []}

    if rutas:
        for ruta in rutas:
            reservasInfo = ruta.get('reservasInfo', [])
            if reservasInfo:
                for reserva in reservasInfo:
                    resena_texto = reserva.get('reseña')
                    if resena_texto: 
                        contexto['resenas'].append({
                            'id': str(ruta['_id']),
                            'email': reserva.get('email'),
                            'resena': resena_texto,
                            'tipo': 'conductor'
                        })

            pasajerosInfo = ruta.get('cumplioRutaInfoPasajeros', [])
            if pasajerosInfo:
                for pasajero in pasajerosInfo:
                    resena_texto = pasajero.get('reseña')
                    if resena_texto:
                        contexto['resenas'].append({
                            'id': str(ruta['_id']),
                            'email': pasajero.get('email'),
                            'resena': resena_texto,
                            'tipo': 'pasajero'
                        })
    if usuario:
        contexto.update({
            'rol': usuario.get('rol'),
            'image_data': usuario.get('foto'),
            'usuario': usuario
        })

    return render(request, 'accounts/resena.html', contexto)





    



'''..............................................gestión de usuarios y administradores....................................................................'''

def eliminar_usuario(request, email):

    if not firebase_admin._apps:
        cred = credentials.Certificate('gouv2-b5056-firebase-adminsdk-mrmlq-7abf803639.json')
        firebase_admin.initialize_app(cred)
    
    try:
        user_record = auth.get_user_by_email(email)
        auth.delete_user(user_record.uid)

        usuarios_collection = db['Usuarios']
        invitados_collection = db['UsuarioInvitado']

        result_usuarios = usuarios_collection.delete_one({'email': email})
        result_invitados = invitados_collection.delete_one({'email': email})

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
    if not firebase_admin._apps:
        cred = credentials.Certificate('gouv2-b5056-firebase-adminsdk-mrmlq-7abf803639.json')
        firebase_admin.initialize_app(cred)

    try:
        user_record = auth.get_user_by_email(email)

        usuarios_collection = db['Usuarios']
        invitados_collection = db['UsuarioInvitado']

        result_usuarios = usuarios_collection.update_one(
            {'email': email},
            {'$set': {'bloqueado': True}}
        )

        result_invitados = invitados_collection.update_one(
            {'email': email},
            {'$set': {'bloqueado': True}}
        )

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
    if not firebase_admin._apps:
        cred = credentials.Certificate('gouv2-b5056-firebase-adminsdk-mrmlq-7abf803639.json')
        firebase_admin.initialize_app(cred)

    try:
        user_record = auth.get_user_by_email(email)

        usuarios_collection = db['Usuarios']
        invitados_collection = db['UsuarioInvitado']

        result_usuarios = usuarios_collection.update_one(
            {'email': email},
            {'$set': {'bloqueado': False}}
        )

        result_invitados = invitados_collection.update_one(
            {'email': email},
            {'$set': {'bloqueado': False}}
        )

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



import firebase_admin
from firebase_admin import credentials, auth

def bloquear_admin(request, email):
    if not firebase_admin._apps:
        cred = credentials.Certificate('gou-adm-firebase-adminsdk-3hxpk-c216f44ec9.json')
        firebase_admin.initialize_app(cred)

    try:
        user_record = auth.get_user_by_email(email)

        auth.update_user(user_record.uid, disabled=True)

        collection = db['GoUadmin']
        result = collection.update_one({'correo': email}, {'$set': {'bloqueado': True}})

        if result.matched_count > 0:
            messages.success(request, 'El administrador se bloqueó correctamente en Firebase y MongoDB.')
        else:
            messages.warning(request, 'El administrador fue bloqueado en Firebase, pero no se encontró en MongoDB.')

    except firebase_admin.exceptions.FirebaseError as e:
        messages.error(request, f'Ocurrió un error al interactuar con Firebase: {e}')
    except Exception as e:
        messages.error(request, f'Ocurrió un error inesperado al bloquear el usuario: {e}')

    return redirect('cuentas')





def desbloquear_admin(request, email):
    if not firebase_admin._apps:
        cred = credentials.Certificate('gou-adm-firebase-adminsdk-3hxpk-c216f44ec9.json')
        firebase_admin.initialize_app(cred)

    try:
        user_record = auth.get_user_by_email(email)

        auth.update_user(user_record.uid, disabled=False)

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
        collection = db['GoUadmin']

        cred = credentials.Certificate("gou-adm-firebase-adminsdk-3hxpk-c216f44ec9.json")
        app = firebase_admin.initialize_app(cred, name='admin_app')

        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        rol = request.POST.get('rol')
        correo = request.POST.get('email')
        password = request.POST.get('password')
       

        try:
            with open('accounts/static/img/administra.jpg', 'rb') as image_file:
                default_image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            administrador = {
                'nombre': nombre,
                'apellido': apellido,
                'rol': rol,
                'correo': correo,
                'foto': default_image_base64,
            }
            collection.insert_one(administrador)

            user = auth.create_user(
                app=app,
                email=correo,
                password=password
            )

            messages.success(request, '¡Administrador creado exitosamente!')
        except Exception as e:
            messages.error(request, f'Error al crear administrador: {str(e)}')
        finally:
            delete_app(app)

    return redirect('cuentas')



def aprobar_registro(request):
    if request.method == 'POST':
        registro_id = request.POST.get('registro_id')

        try:
            object_id = ObjectId(registro_id)
        except Exception as e:
            messages.warning(request, 'Error en registro, no válido')

        collection_registros = db['RegistrosAutos']
        registro = collection_registros.find_one({'_id': object_id})

        if registro:
            collection_registros.update_one({'_id': object_id}, {'$set': {'RespuestaAprobacion': True}})
            messages.warning(request, 'Aprobación exitosa')
            return redirect('documento')
        else:
            messages.warning(request, 'Error en la aprobación')
    else:
        messages.warning(request, 'Error')
        return redirect('documento')



def rechazar_registro(request):
    if request.method == 'POST':
        registro_id = request.POST.get('registro_id')
        motivo_rechazo = request.POST.get('motivo_rechazo', '') 

        try:
            object_id = ObjectId(registro_id)
        except Exception as e:
            messages.warning(request, 'Error al procesar el ID del registro.')
            return redirect('documento')

        collection_registros = db['RegistrosAutos']
        registro = collection_registros.find_one({'_id': object_id})

        if registro:
            update_result = collection_registros.update_one(
                {'_id': object_id}, 
                {'$set': {'Rechazado': True, 'MotivoRechazo': motivo_rechazo}}
            )

            try:
                email = registro.get('email')  

                if email:
                    send_mail(
                        'Notificación de Rechazo de Documento',
                        f'Le informamos que el documento que presentó ha sido rechazado. La razón de este rechazo es la siguiente: {motivo_rechazo}.\n\nSi tiene alguna pregunta o desea obtener más información sobre esta decisión, no dude en ponerse en contacto con nosotros.\n\nAtentamente,\n\nAdministradores GoU V2',
                        'gou2udec@gmail.com',
                        [email],
                        fail_silently=False,
                    )


                    messages.success(request, 'El documento ha sido rechazado y el motivo ha sido enviado por correo electrónico.')
                else:
                    messages.error(request, 'No se pudo enviar el correo electrónico porque el registro no tiene un correo asignado.')
            except Exception as e:
                messages.error(request, 'Error al enviar el correo electrónico.')

            return redirect('documento')
        else:
            messages.warning(request, 'Registro no encontrado.')
            return redirect('documento')
    else:
        messages.warning(request, 'Método no permitido.')
        return redirect('documento')



def gestion_costo_km(request):
    collection = db['Politi_Acuer_otros']

    if request.method == 'POST':
        nuevo_costo_km = float(request.POST.get('kilometro'))
        collection.update_one({}, {"$set": {"Costo_Km": nuevo_costo_km}})

        messages.success(request, 'El costo por kilómetro se ha actualizado exitosamente.')
        return redirect('documento')

    return render(request, 'accounts/gestion_costo_km.html')




def eliminar_resena(request, resena_id, tipo, email):
    collection = db['HistorialDeRutas']

    if tipo == 'conductor':
        result = collection.find_one(
            {'_id': ObjectId(resena_id), 'reservasInfo.email': email}
        )

        if result:
            collection.update_one(
                {'_id': ObjectId(resena_id)},
                {'$pull': {'reservasInfo': {'email': email}}}
            )

    elif tipo == 'pasajero':
        result = collection.find_one(
            {'_id': ObjectId(resena_id), 'cumplioRutaInfoPasajeros.email': email}
        )

        if result:
            collection.update_one(
                {'_id': ObjectId(resena_id)},
                {'$pull': {'cumplioRutaInfoPasajeros': {'email': email}}}
            )

    if email:
        send_mail(
            'Eliminación de Reseña por Infracción de Normas',
            'Le informamos que su reseña ha sido eliminada debido a una infracción de nuestras normas y políticas de uso. '
            'Nuestro equipo ha revisado su contenido y ha determinado que no cumple con los lineamientos establecidos para '
            'la publicación de reseñas en nuestra plataforma.\n\n'
            'Si considera que esta acción ha sido tomada por error o desea presentar una queja o reclamación, no dude en '
            'ponerse en contacto con nosotros a través de este correo: gou2udec@gmail.com. Estaremos encantados de revisar '
            'su caso y proporcionarle más detalles si es necesario.\n\n'
            'Atentamente,\n'
            'Administradores GoU V2',
            'gou2udec@gmail.com',
            [email],
            fail_silently=False,
        )

    return redirect('resena')



def advertir_resena(request, resena_id, tipo, email):
    collection = db['HistorialDeRutas']
    resena_id_obj = ObjectId(resena_id) 

    if tipo == 'conductor':
        collection.update_many(
            {
                '_id': resena_id_obj,
                'reservasInfo.email': email
            },  
            {'$set': {'reservasInfo.$[elem].revisada': True}},
            array_filters=[{'elem.email': email}]
        )

    elif tipo == 'pasajero':
        collection.update_many(
            {
                '_id': resena_id_obj,
                'cumplioRutaInfoPasajeros.email': email
            },  
            {'$set': {'cumplioRutaInfoPasajeros.$[elem].revisada': True}},
            array_filters=[{'elem.email': email}]
        )

    if email:
        send_mail(
            'Advertencia de Reseña',
            'Le informamos que su reseña ha sido revisada y se ha determinado que podría estar infringiendo nuestras normas y políticas de uso. '
            'Le pedimos que tenga precaución con las palabras y el contenido de sus reseñas para cumplir con los lineamientos establecidos en nuestra plataforma.\n\n'
            'Si tiene alguna pregunta o desea discutir esta advertencia, no dude en ponerse en contacto con nosotros a través de este correo: gou2udec@gmail.com.\n\n'
            'Atentamente,\n'
            'Administradores GoU V2',
            'gou2udec@gmail.com',
            [email],
            fail_silently=False,
        )

    return redirect('resena')


def marcar_revisada(request, resena_id, tipo, email):
    collection = db['HistorialDeRutas']
    resena_id_obj = ObjectId(resena_id) 

    if tipo == 'conductor':
        collection.update_many(
            {
                '_id': resena_id_obj,
                'reservasInfo.email': email
            },  
            {'$set': {'reservasInfo.$[elem].revisada': True}},
            array_filters=[{'elem.email': email}]
        )

    elif tipo == 'pasajero':
        collection.update_many(
            {
                '_id': resena_id_obj,
                'cumplioRutaInfoPasajeros.email': email
            },  
            {'$set': {'cumplioRutaInfoPasajeros.$[elem].revisada': True}},
            array_filters=[{'elem.email': email}]
        )

    return redirect('resena')
