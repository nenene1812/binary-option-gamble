import django 
django.setup()
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import trade.routing
from .channelsmiddleware import TokenAuthMiddleware


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_project.settings")

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": TokenAuthMiddleware(
        URLRouter(
            trade.routing.websocket_urlpatterns
        )
    ),
})


# import django 
# django.setup()
# import os

# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.core.asgi import get_asgi_application
# import trade.routing

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_project.settings")

# application = ProtocolTypeRouter({
#   "http": get_asgi_application(),
#   "websocket": AuthMiddlewareStack(
#         URLRouter(
#             trade.routing.websocket_urlpatterns
#         )
#     ),
# })
