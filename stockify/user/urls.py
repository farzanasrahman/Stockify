
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Path to the home view.
    
    path('register/', views.register, name='register'),
    # Path to the registration view.
    
    path('login/', views.login_page, name='login'),
    # Path to the login page view.
    path('profile/', views.profile, name='profile'),         
    # User profile page endpoint
    path('logout/', views.logout_page, name='logout'),      
    # Endpoint to log the user out
    path('profile_update/', views.profile_update, name='profile_update') 
    # Endpoint to update the user's profile
    
]
