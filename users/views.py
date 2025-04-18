from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import UserAccountSerializer
from .models import UserAccount
from rest_framework.permissions import IsAuthenticated


# Create your views here.
@api_view(['POST'])
def create_user(request):
    """
    Crear cuenta nueva.
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
    PRUEBA PARA LOS TOKENS
    """
    # roles = RoleSerializer(UserAccount.objects.all(), many=True).data
    return Response({'message': 'Ruta autorizada'}, status=status.HTTP_200_OK)

@api_view(['POST']) 
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    print(f"Email recibido: {email}")
    print(f"Password recibido: {password}")

    try:
        user = UserAccount.objects.get(email=email)
        print(f"Usuario encontrado: {user.email}")
        print(f"Hash almacenado: {user.password}")
        print(f"check_password result: {user.check_password(password)}")

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
        print("Usuario no encontrado")
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
