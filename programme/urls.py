from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    
    # Inscription flow
    path('inscription/', views.inscription, name='inscription'),
    path('paiement/', views.paiement, name='paiement'),
    path('confirmation/', views.confirmation, name='confirmation'),
    
    # Dashboard Admin
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/action/<int:inscription_id>/<str:action>/', views.dashboard_action, name='dashboard_action'),
]
