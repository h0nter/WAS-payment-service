from rest_framework import serializers


class ConversionSerializer(serializers.Serializer):
    converted_amount = serializers.DecimalField(10, 2)
    conversion_rate = serializers.DecimalField(10, 2)
