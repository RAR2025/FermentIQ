from rest_framework import serializers
from .models import IdealSignature, TankReading, AnalysisResult


class IdealSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdealSignature
        fields = '__all__'


class TankReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TankReading
        fields = '__all__'


class AnalysisResultSerializer(serializers.ModelSerializer):
    status_color = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisResult
        fields = '__all__'

    def get_status_color(self, obj):
        mapping = {
            'perfect': 'green',
            'acceptable': 'blue',
            'concerning': 'orange',
            'failed': 'red'
        }
        return mapping.get(obj.status.lower(), 'grey')
