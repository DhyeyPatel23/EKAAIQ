from django.urls import path
from .views import *
from . import views
from django.shortcuts import render
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('student/signup/', student_signup, name='student_signup'),
    path('teacher/signup/', teacher_signup, name='teacher_signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', login_view, name='login'),
    path('student/home/', home_std , name='student_home'),
    path('teacher/home/', home_tea , name='teacher_home'),
    path('logout/', logout_view , name='logout'),
    path('' , root , name="landing"),
    path('check_prn_exists/', views.check_prn_exists, name='check_prn_exists'),
    path('check_email_exists/', views.check_email_exists, name='check_email_exists'),
    path('check_email_exists_login/', views.check_email_exists_login, name='check_email_exists_login'),
    path('profile/', profile_view, name='profile_view'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('request_password_change/', request_password_change, name='request_password_change'),
    path('verify_password_change_otp/', verify_password_change_otp, name='verify_password_change_otp'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_reset_otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('check_old_password/', check_old_password, name='check_old_password'),
]
