"""
URLs para el módulo de autenticación
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    # Autenticación
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    
    # Gestión de usuarios
    UserListView,
    UserDetailView,
    UserUpdateView,
    ChangePasswordView,
    
    # Gestión de roles
    RolListCreateView,
    RolDetailView,
    PermisoListView,
    
    # Asignación de roles y permisos
    AssignRoleToUserView,
    UserPermissionsView,
    
    # Auditoría y estadísticas
    UserActivityView,
    UserStatsView,
)

app_name = 'authentication'

urlpatterns = [
    # =================== AUTENTICACIÓN ===================
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # =================== GESTIÓN DE USUARIOS ===================
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/change-password/', ChangePasswordView.as_view(), name='user-change-password'),
    
    # =================== GESTIÓN DE ROLES ===================
    path('roles/', RolListCreateView.as_view(), name='rol-list-create'),
    path('roles/<int:pk>/', RolDetailView.as_view(), name='rol-detail'),
    path('permissions/', PermisoListView.as_view(), name='permiso-list'),
    
    # =================== ASIGNACIÓN DE ROLES Y PERMISOS ===================
    path('users/<int:user_id>/assign-role/', AssignRoleToUserView.as_view(), name='assign-role'),
    path('users/<int:user_id>/permissions/', UserPermissionsView.as_view(), name='user-permissions'),
    
    # =================== AUDITORÍA Y ESTADÍSTICAS ===================
    path('activity/', UserActivityView.as_view(), name='activity-list'),
    path('users/<int:user_id>/activity/', UserActivityView.as_view(), name='user-activity'),
    path('stats/', UserStatsView.as_view(), name='user-stats'),
]