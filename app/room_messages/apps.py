from django.apps import AppConfig


class RoomMessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'room_messages'

    def ready(self):
        import room_messages.signals
