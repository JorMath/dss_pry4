# accounts/urls.py
from django.urls import path
from .views import login_view, logout_view, dashboard_jefe, dashboard_analista, dashboard_reportante

urlpatterns = [
    path('login/', login_view, name='login'),
    path('dashboard/jefe/', dashboard_jefe, name='dashboard_jefe'),
    path('dashboard/analista/', dashboard_analista, name='dashboard_analista'),
    path('dashboard/reportante/', dashboard_reportante, name='dashboard_reportante'),
    path('logout/', logout_view, name='logout'),
]
