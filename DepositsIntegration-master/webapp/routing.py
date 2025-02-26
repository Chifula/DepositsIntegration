from channels.routing import ProtocolTypeRouter, ChannelNameRouter
from channels.auth import AuthMiddlewareStack
from channels.sessions import SessionMiddlewareStack
import django_plotly_dash.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        SessionMiddlewareStack(
            django_plotly_dash.routing.application
        )
    ),
})