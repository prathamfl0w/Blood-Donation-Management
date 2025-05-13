from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import BloodRequest, Donation

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'blood_group', 'phone', 'city']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class BloodRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = ['id', 'blood_group', 'status', 'date_requested', 'message']
        read_only_fields = ['id', 'date_requested', 'status']

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ['id', 'blood_group', 'recipient_name', 'date_donated', 'status']
        read_only_fields = ['id', 'date_donated']