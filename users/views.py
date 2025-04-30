from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import UserAccountSerializer, UserProfileSerializer, NotificationSerializer, UserNotificationSerializer
from .models import UserAccount, Notification, UserNotification
from rest_framework.permissions import IsAuthenticated
from logs.utils import get_client_ip
from logs.models import ActivityLog
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials


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
    token = request.data.get('fcm_token')
    print(f"Email recibido: {email}")
    print(f"Password recibido: {password}")

    try:
        user = UserAccount.objects.get(email=email)
        print(f"Usuario encontrado: {user.email}")
        print(f"Hash almacenado: {user.password}")
        print(f"check_password result: {user.check_password(password)}")

        if user.check_password(password):
            if token:
                if user.fcm_token != token:
                    print(f"Actualizando fcm_token de {user.email}")
                    user.fcm_token = token
                    user.save(update_fields=['fcm_token'])
                else:
                    print("El fcm_token recibido es igual al existente. No se actualiza.")

            refresh = RefreshToken.for_user(user)
            return Response({
                'user': {
                    'id': str(user.id),
                    'name': user.name,
                    'email': user.email,
                    'role': user.role
                },
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
    user = request.user
    total_unread = UserNotification.objects.filter(user=user, is_read=False).count()
    notifications = UserNotification.objects.filter(user=user).order_by('-received_at')
    serializer = UserNotificationSerializer(notifications, many=True)
    
    return Response({
        'total_unread': total_unread,
        'notifications': serializer.data
    })


def add_notifications(title, body, type='OTHER', role='ADMIN'):
    users_with_token = UserAccount.objects.filter(fcm_token__isnull=False, role=role).exclude(fcm_token='')
    print(users_with_token)
    tokens = users_with_token.values_list('fcm_token', flat=True)
    try:
        notifications = Notification.objects.create(
            type=type,
            title=title,
            message=body,
            )
        user_notifications = [
            UserNotification(user=user, notification=notifications)
            for user in users_with_token
        ]
        UserNotification.objects.bulk_create(user_notifications)
        send_multicast_notification(
            list(tokens),
            title,
            body
        )
    except Exception as e:
        print(f"Error enviando push a {users_with_token}: {e}")


def send_multicast_notification(tokens, title, body, data=None, role='ADMIN'):
    if not firebase_admin._apps:
        cred = credentials.Certificate("e-commerce.json")
        firebase_admin.initialize_app(cred)
    if not tokens:
        raise ValueError("La lista de tokens está vacía.")

    print("Tokens a enviar:", tokens)
    try:
        for token in tokens:
            individual_message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                token=token,
                data=data or {}
            )
            response = messaging.send(individual_message)
            print(f"Push enviado correctamente a {token}. Response: {response}")
        return response
    except Exception as e:
        print(f"Error enviando push a {tokens}: {e}")
        return None
