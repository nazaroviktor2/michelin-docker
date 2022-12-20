from rest_framework.serializers import ModelSerializer, IntegerField

from card.models import Card, Audio


class CardSerializer(ModelSerializer):

    class Meta:

        model = Card
        fields = "__all__"
        extra_kwargs = {
            'user': {'read_only': True}
        }


class AudioSerializer(ModelSerializer):

    class Meta:
        model = Audio
        fields = "__all__"

        extra_kwargs = {
            'user': {'read_only': True}
        }
