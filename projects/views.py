from rest_framework import viewsets
from .models import Project
from .serializers import ProjectSerializer
from .permissions import IsAdminOrReadOnly, IsAdminUser, AllowAll, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAll]
    authentication_classes = [JWTAuthentication] 

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        elif self.action in ['list', 'retrieve']:
            return [AllowAll()]
        return [IsAuthenticated()]
