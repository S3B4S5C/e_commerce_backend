from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import UserAccountSerializer, UserProfileSerializer, NotificationSerializer
from .models import UserAccount, Notification
from rest_framework.permissions import IsAuthenticated
from logs.utils import get_client_ip
from logs.models import ActivityLog


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def query_profile(request):
    """
    Obtener el perfil del usuario autenticado
    """
    user = request.user
    serializer = UserProfileSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Editar el perfil del usuario autenticado
    """
    user = request.user
    serializer = UserProfileSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Perfil actualizado correctamente',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Permite al usuario cambiar su contraseña proporcionando la contraseña actual.
    """
    user = request.user
    current_password = request.data.get('password')
    new_password = request.data.get('new_password')

    if not current_password or not new_password:
        return Response({'error': 'Se requieren la contraseña actual y la nueva contraseña.'},status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(current_password):
        return Response({'error': 'La contraseña actual no es correcta.'},status=status.HTTP_403_FORBIDDEN)

    user.set_password(new_password)
    user.save()

    return Response({'message': 'Contraseña actualizada exitosamente.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)
