from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('',views.index),
    path('populate/', views.populateDatabase), 
    path('denominacion_vinos/',views.mostrar_vinos_por_denominaciones),
    path('vinos_anyo/',views.buscar_vinos_por_anyo),
    path('vinos_uva/',views.buscar_vinos_por_uva),
    path('admin/',admin.site.urls),

    ]
