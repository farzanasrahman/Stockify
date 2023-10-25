
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Path to the home view.
    
    path('register/', views.register, name='register'),
    # Path to the registration view.
    
    path('login/', views.login_page, name='login')
    # Path to the login page view.
]
