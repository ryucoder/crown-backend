from rest_framework import serializers

from core.models import State, OrderOption


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ["id", "name", "gst_code"]


class OrderOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderOption
        fields = ["id", "option"]


class ServerErrorSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(ServerErrorSerializer, self).__init__(*args, **kwargs)

        for item in self.fields:
            for error_key in self.fields[item].error_messages:
                self.fields[item].error_messages[error_key] = "server_" + error_key

