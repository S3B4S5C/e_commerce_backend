from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from rest_framework import status
from .serializers import UserAccountSerializer, RoleSerializer
from .models import UserAccount
from rest_framework.permissions import IsAuthenticated


# Create your views here.
@api_view(['POST'])
def create_user(request):
    """
    Create a new user account.
    """
    serializer = UserAccountSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        user = UserAccount.objects.get(email=serializer.validated_data['email'])
        user.set_password(user.password)  # Hash the password before saving
        user.save(update_fields=['password'])  # Save the user with the hashed password
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': {
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
            },
            'auth': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Usuario creado exitosamente'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_token(request):
    """
    Get all roles.
    """
    # roles = RoleSerializer(UserAccount.objects.all(), many=True).data
    return Response({'message': 'Ruta autorizada'}, status=status.HTTP_200_OK)

@api_view(['POST']) 
def login_user(request):
    """
    Login a user and return JWT tokens.
    """
    email = request.data.get('email')
    print(email)
    password = request.data['password']
    print(password)
    try:
        user = UserAccount.objects.get(email=email)
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'res': 'Inicio de sesión exitoso',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except UserAccount.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)