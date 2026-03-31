from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('cause/<int:pk>/', views.cause_detail, name='cause_detail'),
    path('cause/<int:pk>/donate/', views.donate, name='donate'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
