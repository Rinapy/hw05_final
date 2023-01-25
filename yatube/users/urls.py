# users/urls.py
from django.contrib.auth import views as auth
from . import views
from django.urls import path, reverse_lazy

app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        auth.LogoutView.as_view(
            template_name='users/logged_out.html'
        ),
        name='logout'
    ),
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'
    ),
    path(
        'login/',
        auth.LoginView.as_view(
            template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_reset/',
        auth.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            email_template_name='users/password_reset_email.html',
            success_url=reverse_lazy('users:password_reset_done')),
        name='password_reset_form'
    ),
    path(

        'password_reset/done',
        auth.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'password_change',
        auth.PasswordChangeView.as_view(
            template_name='users/password_change_form.html',
            success_url=reverse_lazy('users:password_change_done')),
        name='password_change'
    ),
    path(
        'password_change/done',
        auth.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'),
        name='password_change_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_reset_complete')),
        name='password_reset_confrim'
    ),
    path(
        'password_reset_complete',
        auth.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'),
        name='password_reset_complete'
    )
]
