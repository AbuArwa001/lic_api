from django.urls import path, include
from .views import RegisterView, UserProfileView, UserView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
router = DefaultRouter()
router.register(r'', UserView, basename='user')

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(authentication_classes=[]), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('', include(router.urls)),

]
