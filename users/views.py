from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import UserSerializer


# Create your views here.
class UserViewSet(viewsets.ViewSet):

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
