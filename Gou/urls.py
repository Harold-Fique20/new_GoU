from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from accounts import views
from accounts.views import *
from django.conf.urls.static import static


urlpatterns = [
    path('accounts', include('accounts.urls')),
    path('',HomePageView.as_view(), name='index'),
    path('about', AboutPageView.as_view(), name='about'),
    path('descarga', descargaPageView.as_view(), name= 'descarga'),
    path('contact', ContactPageView.as_view(), name='contact'),
    path('admin', admin.site.urls),
    path('login', LoginPageView.as_view(), name='login'),
    path('superadmin', superadminPageView.as_view(), name='superadmin'),
    path('cuentas', views.cuentas, name='cuentas'),
    path('login_view', views.login_view, name='login_view'),
    path('recu_contra', recu_contraPageView.as_view(), name='recu_contra'),
    path('contact', views.send_email, name='send_email'),
    path('config', views.config, name='config'),
    path('usuario', views.usuario, name='usuario'),
    path('eliminar_usuario/<str:uid>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('bloquear_usuario/<str:uid>/', views.bloquear_usuario, name='bloquear_usuario'),
    path('eliminar_admin/<str:uid>/', views.eliminar_admin, name='eliminar_admin'),
    path('bloquear_admin/<str:uid>/', views.bloquear_admin, name='bloquear_admin'),
    path('crear_administrador', views.crear_administrador, name='crear_administrador'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)