from rest_framework import serializers
from .models import Circular

class CircularSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circular
        fields = ["circular_id", "title", "description", "posted_date", "valid_upto", "is_published"]

