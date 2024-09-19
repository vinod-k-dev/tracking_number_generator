from rest_framework import serializers
from tracking.models import TrackingNumber

class TrackingNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingNumber
        fields = ['tracking_number', 'origin_country_id', 'destination_country_id', 'weight', 'created_at', 'customer_id', 'customer_name', 'customer_slug']
