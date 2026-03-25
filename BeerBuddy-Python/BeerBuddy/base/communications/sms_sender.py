from clx.xms import Client
from django.conf import settings


class SMSSender(object):
    def __init__(self, to, message, sender=settings.CLX_MBLOX_DYNAMIC_SENDER_ID):
        self._to = to
        self._sender = sender
        self._message = message

    def send(self):
        client = Client(settings.CLX_MBLOX_SERVICEPLAN, settings.CLX_MBLOX_TOKEN)
        response = None
        try:
            response = client.create_text_message(
                sender=self._sender,
                recipient=self._to,
                body=self._message
            )
        except:
            pass
        return response
