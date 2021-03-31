from flask_socketio import Namespace, emit
from app import socks


class NamespaceTest(Namespace):

    # noinspection PyMethodMayBeStatic
    def on_connect(self):
        print("on connect namespacetest")
        pass

    # noinspection PyMethodMayBeStatic
    def on_disconnect(self):
        print("on disconnect namespacetest")
        pass

    # noinspection PyMethodMayBeStatic
    def on_my_event(self, data):
        print("on my event namespacetest")
        emit('my_response', data)


socks.on_namespace(NamespaceTest('/test'))
