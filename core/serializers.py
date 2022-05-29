from pprint import pprint

from rest_framework import serializers

from core.models import City, District, State, JobType


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "district"]


class DistrictSerializer(serializers.ModelSerializer):
    cities = CitySerializer(many=True)

    class Meta:
        model = District
        fields = ["id", "name", "state", "cities"]


class StateSerializer(serializers.ModelSerializer):

    districts = DistrictSerializer(many=True)

    class Meta:
        model = State
        fields = ["id", "name", "gst_code", "districts"]


class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = ["id", "option"]


class ServerErrorSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super(ServerErrorSerializer, self).__init__(*args, **kwargs)

        for item in self.fields:
            for error_key in self.fields[item].error_messages:
                self.fields[item].error_messages[error_key] = "server_" + error_key


class ServerErrorModelSerializer(serializers.ModelSerializer):
    """
    TODO: Need to fix and use everywhere
    Not working for ModelSerializer
    When instantiated, errors get updated.
    But when the errors are returned to user, they are the default error messages.
    """

    def __init__(self, *args, **kwargs):
        super(ServerErrorModelSerializer, self).__init__(*args, **kwargs)

        for item in self.fields:
            for error_key in self.fields[item].error_messages:
                self.fields[item].error_messages[error_key] = "server_" + error_key
