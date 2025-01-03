from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import bcrypt
def _create_hash(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def _genJwt(user):
    refresh = RefreshToken.for_user(user)
    
    refresh.payload["role"] = user.role

    return Response({
        "message": "Login successful.",
        "user": user.username,
        "token": str(refresh.access_token) 
    }, status=status.HTTP_200_OK)

def _compare_hash(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))