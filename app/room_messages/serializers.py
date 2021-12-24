import datetime

from rest_framework import serializers
from room_messages.models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.id')

    class Meta:
        model = Message
        fields = ('id', 'text', 'room', 'sender', 'created_at', 'updated_at')

        extra_kwargs = {'created_at': {'read_only': True},
                        'updated_at': {'read_only': True}}

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields()
        request = self.context.get('request', None)
        if request and (request.method in ('PUT', 'PATCH')):
            fields['room'].read_only = True
        return fields

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.updated_at = datetime.datetime.utcnow()
        instance.save()

        return instance


class ListMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('text', 'sender', 'created_at', 'updated_at')
