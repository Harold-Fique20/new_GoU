from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from accounts import views
from accounts.views import *
from django.conf.urls.static import static


urlpatterns = [
    # Paths para la aplicación
    path('accounts', include('accounts.urls')),
    path('admin', admin.site.urls),

    # Paths para las vistas generales
    path('',HomePageView.as_view(), name='index'),
    path('about', AboutPageView.as_view(), name='about'),
    path('descarga', descargaPageView.as_view(), name= 'descarga'),
    path('contact', ContactPageView.as_view(), name='contact'),
    path('contact/', send_email, name='send_email'),
    path('login', LoginPageView.as_view(), name='login'),
    path('principal', views.principal, name='principal'),
    path('recu_contra', recu_contraPageView.as_view(), name='recu_contra'),

    # Paths para las vistas específicas
    path('cuentas', views.cuentas, name='cuentas'),
    path('login_view', views.login_view, name='login_view'),
    path('config', views.config, name='config'),
    path('usuario', views.usuario, name='usuario'),
    path('documento', views.documento, name='documento'),
    path('resena', views.resena, name='resena'),

    # Paths para la gestión de usuarios y administradores
    path('eliminar_usuario/<str:email>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('bloquear_usuario/<str:email>/', views.bloquear_usuario, name='bloquear_usuario'),
    path('desbloquear_usuario/<str:email>/', views.desbloquear_usuario, name='desbloquear_usuario'),
    path('eliminar_admin/<str:email>/', views.eliminar_admin, name='eliminar_admin'),
    path('bloquear_admin/<str:email>/', views.bloquear_admin, name='bloquear_admin'),
    path('desbloquear_admin/<str:email>/', views.desbloquear_admin, name='desbloquear_admin'),
    path('crear_administrador', views.crear_administrador, name='crear_administrador'),
    path('aprobar_registro', aprobar_registro, name='aprobar_registro'),
    path('rechazar_registro', rechazar_registro, name='rechazar_registro'),
    path('gestion-costo-km/', views.gestion_costo_km, name='gestion_costo_km'),
    path('resenas/eliminar/<str:resena_id>/<str:tipo>/<str:email>/', views.eliminar_resena, name='eliminar_resena'),
    path('resenas/advertir/<str:resena_id>/<str:tipo>/<str:email>/', views.advertir_resena, name='advertir_resena'),
    path('resenas/revisada/<str:resena_id>/<str:tipo>/<str:email>/', views.marcar_revisada, name='marcar_revisada'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)