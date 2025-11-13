from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView, LoginView, UserProfileView, UserView

urlpatterns = [
    # Django ORM + JWT authentication (existing)
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserView.as_view(), name='user-profile'),
    path('token/', TokenRefreshView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # Raw SQL + Token authentication (new)
    path('auth/', include('users.raw_sql_auth.urls')),
]
