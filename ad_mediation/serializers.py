from rest_framework import serializers
from .models import Backend


class BackendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backend
        fields = '__all__'
