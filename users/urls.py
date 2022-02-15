from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="signup"),
    path(
        "logout/",
        LogoutView.as_view(template_name='registration/logged_out.html'),
        name="logout"
    ),
    path(
        "login/",
        LoginView.as_view(template_name='registration/login.html'),
        name="login"
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name='registration/password_reset_form.html'
        ),
        name='password_reset'
    ),
]
