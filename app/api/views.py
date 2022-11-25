from django.shortcuts import render

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import Vehicule
from .serializers import (
    RegistrationSerializer,
    PasswordChangeSerializer,
    VehiculeSerializer,
)


@api_view(["GET"])
def getRoutes(request):
    routes = [
        "http://localhost:8000/v1/accounts/register/",
        "http://localhost:8000/v1/accounts/login/",
        "http://localhost:8000/v1/accounts/logout/",
        "http://localhost:8000/v1/accounts/change-password/",
        "http://localhost:8000/v1/vehicules/",
        "http://localhost:8000/v1/token/",
        "http://localhost:8000/v1/token/refresh/",
    ]

    return Response(routes)


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        if "email" not in request.data or "password" not in request.data:
            return Response(
                {"msg": "Credentials missing"}, status=status.HTTP_400_BAD_REQUEST
            )
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            auth_data = get_tokens_for_user(request.user)
            return Response(
                {"msg": "Login Success", **auth_data}, status=status.HTTP_200_OK
            )
        return Response(
            {"msg": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"msg": "Successfully Logged out"}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            context={"request": request}, data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )  # Another way to write is as in Line 17
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VehiculeViewset(ModelViewSet):
    serializer_class = VehiculeSerializer

    def get_queryset(self):
        queryset = Vehicule.objects.all()

        marque = self.request.GET.get("marque")

        if marque is not None:
            queryset = queryset.filter(marque=marque)

        return queryset
