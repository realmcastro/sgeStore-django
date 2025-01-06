import jwt
from django.conf import settings
from functools import wraps
from django.http import HttpResponseForbidden, JsonResponse
from rest_framework.exceptions import AuthenticationFailed

def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            token = request.headers.get('Authorization', None)
            
            if not token:
                return HttpResponseForbidden("Token de autorização não encontrado.")
            
            token = token.split(' ')[1] if token.startswith('Bearer ') else token
            
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                
                user_role = payload.get('role', None)

                if required_role == 'admin' and user_role != 'admin':
                    return JsonResponse({"error":"Você precisa ser administrador para acessar essa página."}, status=403)
                elif required_role == 'mod' and user_role not in ['admin', 'mod']:
                    return JsonResponse({"error":"Você precisa ser moderador ou administrador para acessar essa página."},status=403)
                elif required_role == 'user' and user_role not in ['admin', 'mod', 'user']:
                    return JsonResponse({"error":"Você precisa ser administrador, moderador ou usuário para acessar essa página."}, status=403)
            
            except jwt.ExpiredSignatureError:
                return HttpResponseForbidden("Token expirado.", status=403)
            except jwt.InvalidTokenError:
                return HttpResponseForbidden("Token inválido.", status=403)
            
            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator
