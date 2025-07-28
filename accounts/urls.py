# accounts/urls.py
from django.urls import path
from .views import (login_view, logout_view, dashboard_jefe, dashboard_analista, 
                   dashboard_reportante, forgot_password_view, rate_limit_exceeded_view,
                   forgot_password_rate_limit_view)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('rate-limit-exceeded/', rate_limit_exceeded_view, name='rate_limit_exceeded'),
    path('forgot-password-rate-limit/', forgot_password_rate_limit_view, name='forgot_password_rate_limit'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('dashboard/jefe/', dashboard_jefe, name='dashboard_jefe'),
    path('dashboard/analista/', dashboard_analista, name='dashboard_analista'),
    path('dashboard/reportante/', dashboard_reportante, name='dashboard_reportante'),
    path('logout/', logout_view, name='logout'),
]
