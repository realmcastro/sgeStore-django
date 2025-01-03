from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.timezone import now
from sgeStore.decorators import role_required
from sgeStore.auth_service import _create_hash, _genJwt, _compare_hash
from .models import CustomUser

@role_required('admin')
@api_view(['POST'])
def create_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
    
    hashed_password = _create_hash(password)
    
    hasUser = CustomUser.objects.filter(username=username).exists()
    if hasUser:
        return Response({"error": "Username is already used by another user."}, status=status.HTTP_400_BAD_REQUEST)
    
    user = CustomUser(username=username, password=hashed_password)
    user.save()

    return Response({"username": user.username, "id": user.id}, status=status.HTTP_201_CREATED)

@role_required('admin')
@api_view(['DELETE'])
def delete_user(request):
    user_id = request.data.get('user_id')

    if not user_id:
        return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

@role_required('mod')
@api_view(['PUT'])
def update_password(request):
    new_password = request.data.get('new_password')
    user_id = request.data.get('user_id')
    
    if not new_password:
        return Response({"error": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(id=user_id)

        hashed_password = _create_hash(new_password)
        user.password = hashed_password
        user.save()
        return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
    
    if len(password) < 8:
        return Response({"error": "Password must be at least 8 characters long."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(username=username)
        if _compare_hash(user.password, password):
            user.last_login = now()
            user.save()
            return _genJwt(user)
        else:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
