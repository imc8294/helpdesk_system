from drf_yasg.utils import swagger_auto_schema
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer
from .models import CustomUser
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import GenericAPIView


class UserProfileView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_summary="Logged in user can view their profile details here, email and role are read-only",
        responses={200: UserSerializer, 404: "User not found", 401: "Authentication credentials were not provided."}
    )
    def get(self, request):
        users = CustomUser.objects.get(email=request.user.email)
        serializer = self.serializer_class(users)
        return Response(serializer.data, status=status.HTTP_200_OK) 
    
    @swagger_auto_schema(
        operation_summary="Logged in user can Update their profile details here",
        responses={200: UserSerializer, 404: "User not found"}
    )
    def patch(self, request):
        try:
            user = CustomUser.objects.get(email=request.user.email)
            serializer = self.serializer_class(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @swagger_auto_schema(
        operation_summary="Logged in user can delete their profile here",
        responses={
            200: "User deleted successfully", 404: "User not found",
            401: "Authentication credentials were not provided."
        }
    )
    def delete(self, request):
        try:
            user = CustomUser.objects.get(email=request.user.email)
            user.is_active = False
            user.save()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
class UserRegisterView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer

    @swagger_auto_schema(
        operation_summary="User can register here with email, password, first_name, last_name and role",
        responses={201: "User registered successfully", 400: "Bad Request"}
    )
    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    
    @swagger_auto_schema(
        operation_summary="Admin, Agent and User can login here and use the token to access the ticket APIs",
        responses={200: "Login Successfully ", 401: "Invalid credentials or User not found"}
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'action': 'login'})
        user = serializer.authenticate(
            email=request.data.get('email'),
            password=request.data.get('password')
        )
        if user:
            auth_token = RefreshToken.for_user(user)
            response = {
                'status': True,
                'user_id': user.id,
                'message': 'Login Successfully',
                'access_token': str(auth_token.access_token)
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials or User not found'}, status=status.HTTP_401_UNAUTHORIZED)
    
