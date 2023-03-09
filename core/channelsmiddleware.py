
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.authtoken.models import Token

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.db import close_old_connections
import urllib.parse
from user.models import User
from jwt import decode as jwt_decode
from django.conf import settings

@database_sync_to_async
def get_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        return user
    except user.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner
    def __call__(self, scope):
        return TokenAuthMiddlewareInstance(scope, self)


class TokenAuthMiddlewareInstance:
    """
    Yeah, this is black magic:
    https://github.com/django/channels/issues/1399
    """
    def __init__(self, scope, middleware):
        self.middleware = middleware
        self.scope = dict(scope)
        self.inner = self.middleware.inner

    async def __call__(self, receive, send):
        close_old_connections()
        token = urllib.parse.parse_qs(self.scope["query_string"].decode("utf8"))["token"][0]
        try:
            # This will automatically validate the token and raise an error if token is invalid
            UntypedToken(token)
        except (InvalidToken, TokenError) as e:
            # Token is invalid
            print(e)
            return None
        else:
            
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_data['user_id']
            self.scope['user'] = await get_user(user_id)
        # decoded_qs = urllib.parse.parse_qs(self.scope["query_string"])
        # print(decoded_qs)
        # if b'token' in decoded_qs:
        #   token = decoded_qs.get(b'token').pop().decode()
        #   print(token)
        #   self.scope['user'] = await get_user(token)
        #   print(self.scope['user'])

        return await self.inner(self.scope, receive, send)


TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))