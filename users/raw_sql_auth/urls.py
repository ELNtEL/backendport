"""
URL configuration for raw SQL authentication endpoints
"""
from django.urls import path
from . import views, examples

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_view, name='raw_sql_register'),
    path('login/', views.login_view, name='raw_sql_login'),
    path('logout/', views.logout_view, name='raw_sql_logout'),
    path('me/', views.user_info_view, name='raw_sql_user_info'),

    # Example protected endpoints
    path('protected/', examples.protected_view, name='raw_sql_protected'),
    path('optional/', examples.optional_auth_view, name='raw_sql_optional'),
    path('protected-action/', examples.protected_post_example, name='raw_sql_protected_action'),
]
