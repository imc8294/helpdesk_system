
from django.urls import path, include
from .views import LoginView, UserRegisterView, UserProfileView
from .filter_user_view import UserFilterView

urlpatterns = [
    path('Login', LoginView.as_view(), name='login'),
    path('Register', UserRegisterView.as_view(), name='register'),
    path('Profile', UserProfileView.as_view(), name='profile'),
    path('ListFilter', UserFilterView.as_view(), name='all-users'),
]
